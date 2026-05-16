from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

try:
    import joblib
    import numpy as np
    import pandas as pd
    from scipy import sparse
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    ML_STACK_AVAILABLE = True
    ML_IMPORT_ERROR = None
except ImportError as exc:  # pragma: no cover - depends on deployment environment
    joblib = None
    np = None
    pd = None
    sparse = None
    TfidfVectorizer = None
    cosine_similarity = None
    ML_STACK_AVAILABLE = False
    ML_IMPORT_ERROR = exc

from store.models import Product, Recommendation, UserInteraction

logger = logging.getLogger(__name__)

INTERACTION_WEIGHTS = {
    "view": 1.0,
    "click": 2.0,
    "cart": 4.0,
    "purchase": 6.0,
    "search": 1.5,
    "like": 2.5,
}

ARTIFACT_RELATIVE_DIR = Path("models") / "recommender"
ARTIFACT_VERSION = 1
DEFAULT_TOP_K = 12

MIN_CF_EVENTS = 30
MIN_CF_ACTORS = 5
MIN_CF_PRODUCTS = 8

CONFIG_FILE = "config.json"
METRICS_FILE = "metrics.json"
PRODUCT_MAP_FILE = "product_id_map.json"
USER_PROFILES_FILE = "user_profiles.json"
POPULARITY_FILE = "popularity.json"
VECTORIZER_FILE = "vectorizer.joblib"
PRODUCT_MATRIX_FILE = "product_matrix.joblib"
ITEM_SIMILARITY_FILE = "item_similarity.joblib"

_ARTIFACT_CACHE = {
    "trained_at": None,
    "data": None,
}


def _recommendable_product_q() -> Q:
    return Q(is_available=True) & (Q(manages_local_stock=False) | Q(stock_level__gt=0))


def _artifact_dir() -> Path:
    return Path(settings.BASE_DIR) / ARTIFACT_RELATIVE_DIR


def _to_actor_key(user_id: Optional[int] = None, session_key: Optional[str] = None) -> Optional[str]:
    if user_id:
        return f"u:{user_id}"
    if session_key:
        return f"s:{session_key}"
    return None


def _normalize_limit(limit: int) -> int:
    try:
        parsed = int(limit)
    except (TypeError, ValueError):
        return DEFAULT_TOP_K
    return max(1, parsed)


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clear_artifact_cache() -> None:
    _ARTIFACT_CACHE["trained_at"] = None
    _ARTIFACT_CACHE["data"] = None


def _require_ml_stack() -> None:
    if not ML_STACK_AVAILABLE:
        raise RuntimeError(
            "The optional recommender training dependencies are not installed. "
            "Install them with: pip install -r requirements-ml.txt"
        ) from ML_IMPORT_ERROR


def _build_product_frame() -> pd.DataFrame:
    _require_ml_stack()
    rows = Product.objects.filter(is_available=True).select_related("category").values(
        "product_id",
        "name",
        "description",
        "category_id",
        "category__name",
        "rating",
    )
    if not rows:
        return pd.DataFrame(
            columns=["product_id", "name", "description", "category_id", "category_name", "rating", "text"]
        )

    df = pd.DataFrame(rows)
    df.rename(columns={"category__name": "category_name"}, inplace=True)
    df["name"] = df["name"].fillna("")
    df["description"] = df["description"].fillna("")
    df["category_name"] = df["category_name"].fillna("")
    df["rating"] = df["rating"].fillna(0)
    df["text"] = (df["name"] + " " + df["category_name"] + " " + df["description"]).str.strip()
    return df


def _build_interaction_frame(valid_product_ids: set[int]) -> pd.DataFrame:
    _require_ml_stack()
    rows = UserInteraction.objects.filter(product__isnull=False).values(
        "user_id",
        "session_key",
        "product_id",
        "interaction_type",
        "interaction_count",
        "timestamp",
        "query",
        "metadata",
    )
    if not rows:
        return pd.DataFrame(
            columns=["actor_key", "product_id", "interaction_type", "interaction_count", "weight", "timestamp"]
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(
            columns=["actor_key", "product_id", "interaction_type", "interaction_count", "weight", "timestamp"]
        )

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df = df[df["timestamp"].notna()].copy()
    df = df[df["product_id"].isin(valid_product_ids)].copy()

    def build_actor(row):
        if pd.notna(row.get("user_id")):
            return _to_actor_key(user_id=int(row["user_id"]))
        session_key = row.get("session_key")
        if isinstance(session_key, str) and session_key.strip():
            return _to_actor_key(session_key=session_key.strip())
        return None

    df["actor_key"] = df.apply(build_actor, axis=1)
    df = df[df["actor_key"].notna()].copy()

    df["interaction_count"] = pd.to_numeric(df["interaction_count"], errors="coerce").fillna(1).clip(lower=1)
    df["base_weight"] = df["interaction_type"].map(INTERACTION_WEIGHTS).fillna(1.0)
    df["weight"] = df["base_weight"] * df["interaction_count"]

    return df[["actor_key", "product_id", "interaction_type", "interaction_count", "weight", "timestamp"]]


def temporal_split_interactions(
    interactions_df: pd.DataFrame,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
) -> Dict[str, object]:
    _require_ml_stack()
    empty_df = pd.DataFrame(
        columns=["actor_key", "product_id", "interaction_type", "interaction_count", "weight", "timestamp"]
    )
    if interactions_df is None or interactions_df.empty:
        return {
            "train": empty_df.copy(),
            "validation": empty_df.copy(),
            "test": empty_df.copy(),
            "meta": {
                "train_count": 0,
                "validation_count": 0,
                "test_count": 0,
                "train_cutoff": None,
                "validation_cutoff": None,
                "latest_timestamp": None,
            },
        }

    df = interactions_df.sort_values("timestamp").reset_index(drop=True)
    total = len(df)

    if total == 1:
        train_end = 1
        val_end = 1
    else:
        train_end = max(1, min(total - 1, int(total * train_ratio)))
        val_end = max(train_end + 1, int(total * (train_ratio + val_ratio)))
        val_end = min(val_end, total)

    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()

    return {
        "train": train_df,
        "validation": val_df,
        "test": test_df,
        "meta": {
            "train_count": int(len(train_df)),
            "validation_count": int(len(val_df)),
            "test_count": int(len(test_df)),
            "train_cutoff": train_df["timestamp"].max().isoformat() if not train_df.empty else None,
            "validation_cutoff": val_df["timestamp"].max().isoformat() if not val_df.empty else None,
            "latest_timestamp": df["timestamp"].max().isoformat() if not df.empty else None,
        },
    }


def _normalize_score_map(score_map: Dict[int, float]) -> Dict[int, float]:
    if not score_map:
        return {}
    max_value = max(score_map.values())
    if max_value <= 0:
        return {pid: 0.0 for pid in score_map}
    return {pid: float(score) / float(max_value) for pid, score in score_map.items()}


def _build_training_profiles(train_df: pd.DataFrame, product_frame: pd.DataFrame) -> Dict[str, object]:
    _require_ml_stack()
    actor_product_weights: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
    actor_purchases: Dict[str, set[int]] = defaultdict(set)
    actor_category_affinity: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))

    product_category_map = {
        int(row.product_id): int(row.category_id) if pd.notna(row.category_id) else None
        for row in product_frame.itertuples()
    }

    for row in train_df.itertuples(index=False):
        actor_key = row.actor_key
        product_id = int(row.product_id)
        weight = float(row.weight)

        actor_product_weights[actor_key][product_id] += weight
        category_id = product_category_map.get(product_id)
        if category_id is not None:
            actor_category_affinity[actor_key][category_id] += weight

        if row.interaction_type == "purchase":
            actor_purchases[actor_key].add(product_id)

    normalized_affinity: Dict[str, Dict[int, float]] = {}
    for actor_key, category_scores in actor_category_affinity.items():
        total = sum(category_scores.values())
        if total <= 0:
            normalized_affinity[actor_key] = {}
            continue
        normalized_affinity[actor_key] = {
            int(category_id): float(score / total) for category_id, score in category_scores.items()
        }

    return {
        "actor_product_weights": {
            actor_key: {int(pid): float(score) for pid, score in product_scores.items()}
            for actor_key, product_scores in actor_product_weights.items()
        },
        "actor_category_affinity": normalized_affinity,
        "actor_purchases": {
            actor_key: sorted(int(pid) for pid in product_ids) for actor_key, product_ids in actor_purchases.items()
        },
    }


def _build_popularity_scores(train_df: pd.DataFrame) -> Dict[int, float]:
    _require_ml_stack()
    if train_df.empty:
        return {}
    grouped = train_df.groupby("product_id")["weight"].sum().to_dict()
    return _normalize_score_map({int(pid): float(score) for pid, score in grouped.items()})


def _build_content_artifacts(product_frame: pd.DataFrame) -> Tuple[TfidfVectorizer, sparse.csr_matrix]:
    _require_ml_stack()
    product_texts = product_frame["text"].fillna("").astype(str).tolist()
    if not product_texts:
        vectorizer = TfidfVectorizer(max_features=1)
        vectorizer.fit(["placeholder"])
        return vectorizer, sparse.csr_matrix((0, len(vectorizer.get_feature_names_out())))

    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform(product_texts)
    except ValueError:
        vectorizer = TfidfVectorizer(max_features=5000)
        matrix = vectorizer.fit_transform(product_texts)
    return vectorizer, matrix.tocsr()


def _build_collaborative_artifacts(train_df: pd.DataFrame, product_ids: List[int]) -> Optional[sparse.csr_matrix]:
    _require_ml_stack()
    if train_df.empty:
        return None

    actor_ids = sorted(train_df["actor_key"].unique().tolist())
    if len(actor_ids) < MIN_CF_ACTORS or len(product_ids) < MIN_CF_PRODUCTS or len(train_df) < MIN_CF_EVENTS:
        return None

    actor_index = {actor_key: idx for idx, actor_key in enumerate(actor_ids)}
    product_index = {int(pid): idx for idx, pid in enumerate(product_ids)}

    grouped = train_df.groupby(["actor_key", "product_id"])["weight"].sum().reset_index()
    rows = grouped["actor_key"].map(actor_index).to_numpy(dtype=int)
    cols = grouped["product_id"].map(lambda pid: product_index[int(pid)]).to_numpy(dtype=int)
    data = grouped["weight"].astype(float).to_numpy()

    actor_item_matrix = sparse.csr_matrix((data, (rows, cols)), shape=(len(actor_ids), len(product_ids)))
    if actor_item_matrix.nnz == 0:
        return None

    similarity = cosine_similarity(actor_item_matrix.T, dense_output=False)
    return similarity.tocsr()


def _serialize_profiles_for_artifact(profiles: Dict[str, object]) -> Dict[str, object]:
    return {
        "actor_product_weights": {
            actor_key: {str(pid): float(score) for pid, score in product_scores.items()}
            for actor_key, product_scores in profiles.get("actor_product_weights", {}).items()
        },
        "actor_category_affinity": {
            actor_key: {str(category_id): float(score) for category_id, score in category_scores.items()}
            for actor_key, category_scores in profiles.get("actor_category_affinity", {}).items()
        },
        "actor_purchases": {
            actor_key: [int(pid) for pid in product_ids]
            for actor_key, product_ids in profiles.get("actor_purchases", {}).items()
        },
    }


def _deserialize_profiles(raw_profiles: Dict[str, object]) -> Dict[str, object]:
    return {
        "actor_product_weights": {
            actor_key: {int(pid): float(score) for pid, score in product_scores.items()}
            for actor_key, product_scores in raw_profiles.get("actor_product_weights", {}).items()
        },
        "actor_category_affinity": {
            actor_key: {int(category_id): float(score) for category_id, score in category_scores.items()}
            for actor_key, category_scores in raw_profiles.get("actor_category_affinity", {}).items()
        },
        "actor_purchases": {
            actor_key: [int(pid) for pid in product_ids]
            for actor_key, product_ids in raw_profiles.get("actor_purchases", {}).items()
        },
    }


def _prepare_artifact_payload(
    product_frame: pd.DataFrame,
    profiles: Dict[str, object],
    popularity_scores: Dict[int, float],
    vectorizer: Optional[TfidfVectorizer],
    product_matrix: Optional[sparse.csr_matrix],
    item_similarity: Optional[sparse.csr_matrix],
    split_meta: Dict[str, object],
    train_ratio: float,
    val_ratio: float,
    top_k: int,
) -> Dict[str, object]:
    _require_ml_stack()
    product_ids = [int(pid) for pid in product_frame["product_id"].tolist()]
    product_index = {str(pid): idx for idx, pid in enumerate(product_ids)}
    product_category_map = {
        str(int(row.product_id)): int(row.category_id) if pd.notna(row.category_id) else None
        for row in product_frame.itertuples()
    }

    trained_at = timezone.now().isoformat()
    config = {
        "artifact_version": ARTIFACT_VERSION,
        "trained_at": trained_at,
        "train_ratio": float(train_ratio),
        "validation_ratio": float(val_ratio),
        "test_ratio": float(max(0.0, 1.0 - train_ratio - val_ratio)),
        "top_k": int(top_k),
        "weights": INTERACTION_WEIGHTS,
        "split": split_meta,
        "collaborative_filtering_enabled": bool(item_similarity is not None),
    }

    return {
        "trained_at": trained_at,
        "config": config,
        "product_map": {
            "product_ids": product_ids,
            "product_index": product_index,
            "product_category_map": product_category_map,
        },
        "user_profiles": _serialize_profiles_for_artifact(profiles),
        "popularity": {str(pid): float(score) for pid, score in popularity_scores.items()},
        "vectorizer": vectorizer,
        "product_matrix": product_matrix,
        "item_similarity": item_similarity,
    }


def _save_artifacts(payload: Dict[str, object], metrics: Dict[str, object]) -> None:
    _require_ml_stack()
    artifact_dir = _artifact_dir()
    artifact_dir.mkdir(parents=True, exist_ok=True)

    (artifact_dir / CONFIG_FILE).write_text(json.dumps(payload["config"], indent=2), encoding="utf-8")
    (artifact_dir / PRODUCT_MAP_FILE).write_text(json.dumps(payload["product_map"], indent=2), encoding="utf-8")
    (artifact_dir / USER_PROFILES_FILE).write_text(json.dumps(payload["user_profiles"], indent=2), encoding="utf-8")
    (artifact_dir / POPULARITY_FILE).write_text(json.dumps(payload["popularity"], indent=2), encoding="utf-8")
    (artifact_dir / METRICS_FILE).write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    if payload.get("vectorizer") is not None:
        joblib.dump(payload["vectorizer"], artifact_dir / VECTORIZER_FILE)
    if payload.get("product_matrix") is not None:
        joblib.dump(payload["product_matrix"], artifact_dir / PRODUCT_MATRIX_FILE)
    if payload.get("item_similarity") is not None:
        joblib.dump(payload["item_similarity"], artifact_dir / ITEM_SIMILARITY_FILE)


def _load_artifacts_from_disk() -> Optional[Dict[str, object]]:
    artifact_dir = _artifact_dir()
    config_path = artifact_dir / CONFIG_FILE
    product_map_path = artifact_dir / PRODUCT_MAP_FILE
    user_profiles_path = artifact_dir / USER_PROFILES_FILE
    popularity_path = artifact_dir / POPULARITY_FILE

    required = [config_path, product_map_path, user_profiles_path, popularity_path]
    if not all(path.exists() for path in required):
        return None

    config = json.loads(config_path.read_text(encoding="utf-8"))
    product_map = json.loads(product_map_path.read_text(encoding="utf-8"))
    raw_profiles = json.loads(user_profiles_path.read_text(encoding="utf-8"))
    popularity_raw = json.loads(popularity_path.read_text(encoding="utf-8"))

    product_ids = [int(pid) for pid in product_map.get("product_ids", [])]
    product_index = {int(pid): int(idx) for pid, idx in product_map.get("product_index", {}).items()}
    product_category_map = {
        int(pid): (int(category_id) if category_id is not None else None)
        for pid, category_id in product_map.get("product_category_map", {}).items()
    }

    vectorizer = None
    product_matrix = None
    item_similarity = None

    vectorizer_path = artifact_dir / VECTORIZER_FILE
    matrix_path = artifact_dir / PRODUCT_MATRIX_FILE
    similarity_path = artifact_dir / ITEM_SIMILARITY_FILE

    if ML_STACK_AVAILABLE:
        if vectorizer_path.exists() and matrix_path.exists():
            vectorizer = joblib.load(vectorizer_path)
            product_matrix = joblib.load(matrix_path)
            if not sparse.issparse(product_matrix):
                product_matrix = sparse.csr_matrix(product_matrix)

        if similarity_path.exists():
            loaded_similarity = joblib.load(similarity_path)
            if loaded_similarity is not None:
                item_similarity = (
                    loaded_similarity
                    if sparse.issparse(loaded_similarity)
                    else sparse.csr_matrix(loaded_similarity)
                )
    elif vectorizer_path.exists() or matrix_path.exists() or similarity_path.exists():
        logger.warning(
            "Recommender ML artifacts exist but optional ML dependencies are not installed; "
            "serving JSON-based popularity/category fallbacks only."
        )

    profiles = _deserialize_profiles(raw_profiles)
    popularity_scores = {int(pid): float(score) for pid, score in popularity_raw.items()}

    return {
        "trained_at": config.get("trained_at"),
        "config": config,
        "product_ids": product_ids,
        "product_index": product_index,
        "product_category_map": product_category_map,
        "profiles": profiles,
        "popularity_scores": popularity_scores,
        "vectorizer": vectorizer,
        "product_matrix": product_matrix,
        "item_similarity": item_similarity,
    }


def load_recommender_artifacts(force_reload: bool = False) -> Optional[Dict[str, object]]:
    if not force_reload and _ARTIFACT_CACHE["data"] is not None:
        return _ARTIFACT_CACHE["data"]

    payload = _load_artifacts_from_disk()
    if payload is None:
        _ARTIFACT_CACHE["trained_at"] = None
        _ARTIFACT_CACHE["data"] = None
        return None

    _ARTIFACT_CACHE["trained_at"] = payload.get("trained_at")
    _ARTIFACT_CACHE["data"] = payload
    return payload


def _build_content_scores(
    actor_key: str,
    product_ids: List[int],
    product_index: Dict[int, int],
    profiles: Dict[str, object],
    product_matrix: Optional[sparse.csr_matrix],
) -> Dict[int, float]:
    if not ML_STACK_AVAILABLE or product_matrix is None:
        return {}

    actor_weights = profiles.get("actor_product_weights", {}).get(actor_key, {})
    if not actor_weights:
        return {}

    valid_history = [(pid, weight) for pid, weight in actor_weights.items() if pid in product_index]
    if not valid_history:
        return {}

    history_indices = [product_index[pid] for pid, _ in valid_history]
    history_weights = np.array([float(weight) for _, weight in valid_history], dtype=float).reshape(-1, 1)
    history_matrix = product_matrix[history_indices]
    weighted_history = history_matrix.multiply(history_weights)
    profile_vector = weighted_history.sum(axis=0)

    if sparse.issparse(profile_vector):
        if profile_vector.nnz == 0:
            return {}
        profile_input = profile_vector
    else:
        profile_input = np.asarray(profile_vector)
        if profile_input.size == 0 or not np.any(profile_input):
            return {}

    similarities = cosine_similarity(profile_input, product_matrix).ravel()
    return {
        pid: float(similarities[product_index[pid]])
        for pid in product_ids
        if pid in product_index and product_index[pid] < len(similarities)
    }


def _build_category_scores(
    actor_key: str,
    product_ids: List[int],
    product_category_map: Dict[int, Optional[int]],
    profiles: Dict[str, object],
) -> Dict[int, float]:
    category_affinity = profiles.get("actor_category_affinity", {}).get(actor_key, {})
    if not category_affinity:
        return {}
    scores = {}
    for product_id in product_ids:
        category_id = product_category_map.get(product_id)
        scores[product_id] = float(category_affinity.get(category_id, 0.0)) if category_id else 0.0
    return scores


def _build_collaborative_scores(
    actor_key: str,
    product_ids: List[int],
    product_index: Dict[int, int],
    profiles: Dict[str, object],
    item_similarity: Optional[sparse.csr_matrix],
) -> Dict[int, float]:
    if not ML_STACK_AVAILABLE or item_similarity is None:
        return {}

    actor_weights = profiles.get("actor_product_weights", {}).get(actor_key, {})
    if not actor_weights:
        return {}

    artifact_size = item_similarity.shape[1]
    scores = np.zeros(artifact_size, dtype=float)
    for history_pid, weight in actor_weights.items():
        if history_pid not in product_index:
            continue
        hist_idx = product_index[history_pid]
        sim_row = item_similarity.getrow(hist_idx)
        if sim_row.nnz == 0:
            continue
        scores[sim_row.indices] += sim_row.data * float(weight)

    return {
        pid: float(scores[product_index[pid]])
        for pid in product_ids
        if pid in product_index and product_index[pid] < len(scores)
    }


def _combine_component_scores(
    product_ids: List[int],
    popularity_scores: Dict[int, float],
    content_scores: Dict[int, float],
    category_scores: Dict[int, float],
    collaborative_scores: Dict[int, float],
    has_history: bool,
) -> Tuple[Dict[int, float], Dict[int, Dict[str, float]]]:
    content_scores = _normalize_score_map(content_scores)
    category_scores = _normalize_score_map(category_scores)
    collaborative_scores = _normalize_score_map(collaborative_scores)

    if has_history:
        weights = {"popularity": 0.2, "content": 0.35, "category": 0.2, "collaborative": 0.25}
    else:
        weights = {"popularity": 1.0, "content": 0.0, "category": 0.0, "collaborative": 0.0}

    final_scores: Dict[int, float] = {}
    score_breakdown: Dict[int, Dict[str, float]] = {}
    for product_id in product_ids:
        components = {
            "popularity": float(popularity_scores.get(product_id, 0.0)),
            "content": float(content_scores.get(product_id, 0.0)),
            "category": float(category_scores.get(product_id, 0.0)),
            "collaborative": float(collaborative_scores.get(product_id, 0.0)),
        }
        score_breakdown[product_id] = components
        final_scores[product_id] = sum(components[name] * weight for name, weight in weights.items())

    return final_scores, score_breakdown


def _reason_from_components(has_history: bool, components: Dict[str, float]) -> str:
    if not has_history:
        return "Popular with shoppers"
    top_component, top_value = max(components.items(), key=lambda item: item[1])
    if top_value <= 0:
        return "Popular with shoppers"
    if top_component == "collaborative":
        return "Similar shoppers liked this"
    if top_component == "content":
        return "Matches products you engaged with"
    if top_component == "category":
        return "Matches your category interests"
    return "Popular with shoppers"


def _recommend_from_artifacts(
    actor_key: Optional[str],
    artifacts: Dict[str, object],
    candidate_ids: List[int],
    limit: int,
    exclude_ids: Optional[set[int]] = None,
) -> List[Dict[str, object]]:
    if not candidate_ids:
        return []

    product_index = artifacts.get("product_index", {})
    popularity_scores = artifacts.get("popularity_scores", {})
    profiles = artifacts.get("profiles", {})
    actor_weights = profiles.get("actor_product_weights", {}).get(actor_key, {}) if actor_key else {}
    has_history = bool(actor_weights)
    artifact_candidate_ids = [int(pid) for pid in candidate_ids if int(pid) in product_index]
    if not artifact_candidate_ids:
        return []

    content_scores = (
        _build_content_scores(
            actor_key=actor_key,
            product_ids=artifact_candidate_ids,
            product_index=product_index,
            profiles=profiles,
            product_matrix=artifacts.get("product_matrix"),
        )
        if actor_key
        else {}
    )
    category_scores = (
        _build_category_scores(
            actor_key=actor_key,
            product_ids=artifact_candidate_ids,
            product_category_map=artifacts.get("product_category_map", {}),
            profiles=profiles,
        )
        if actor_key
        else {}
    )
    collaborative_scores = (
        _build_collaborative_scores(
            actor_key=actor_key,
            product_ids=artifact_candidate_ids,
            product_index=product_index,
            profiles=profiles,
            item_similarity=artifacts.get("item_similarity"),
        )
        if actor_key
        else {}
    )

    final_scores, component_breakdown = _combine_component_scores(
        product_ids=artifact_candidate_ids,
        popularity_scores=popularity_scores,
        content_scores=content_scores,
        category_scores=category_scores,
        collaborative_scores=collaborative_scores,
        has_history=has_history,
    )

    blocked_ids = set(exclude_ids or set())
    if has_history:
        blocked_ids.update(actor_weights.keys())

    ranked_ids = sorted(
        artifact_candidate_ids,
        key=lambda pid: (-_safe_float(final_scores.get(pid, 0.0)), -_safe_float(popularity_scores.get(pid, 0.0)), int(pid)),
    )

    recommendations: List[Dict[str, object]] = []
    for product_id in ranked_ids:
        if product_id in blocked_ids:
            continue
        recommendations.append(
            {
                "product_id": int(product_id),
                "score": float(final_scores.get(product_id, 0.0)),
                "reason": _reason_from_components(has_history, component_breakdown.get(product_id, {})),
            }
        )
        if len(recommendations) >= limit:
            break

    if len(recommendations) < limit and blocked_ids:
        existing_ids = {item["product_id"] for item in recommendations}
        for product_id in ranked_ids:
            if product_id in existing_ids:
                continue
            recommendations.append(
                {
                    "product_id": int(product_id),
                    "score": float(final_scores.get(product_id, 0.0)),
                    "reason": _reason_from_components(has_history, component_breakdown.get(product_id, {})),
                }
            )
            if len(recommendations) >= limit:
                break

    return recommendations


def _fallback_popular_product_ids(candidate_ids: List[int], limit: int) -> List[int]:
    if not candidate_ids:
        return []
    ranked_ids = list(
        Product.objects.filter(product_id__in=candidate_ids)
        .filter(_recommendable_product_q())
        .order_by("-rating", "-stock_level", "product_id")
        .values_list("product_id", flat=True)
    )
    return ranked_ids[:limit]


def _runtime_purchased_ids(user: Optional[User] = None, session_key: Optional[str] = None) -> set[int]:
    filters = {"interaction_type": "purchase"}
    if user is not None:
        filters["user"] = user
    elif session_key:
        filters["session_key"] = session_key
    else:
        return set()

    return set(
        UserInteraction.objects.filter(**filters)
        .exclude(product__isnull=True)
        .values_list("product_id", flat=True)
    )


def recommend_with_scores(
    user: Optional[User] = None,
    session_key: Optional[str] = None,
    limit: int = DEFAULT_TOP_K,
) -> List[Dict[str, object]]:
    limit = _normalize_limit(limit)

    candidate_ids = list(
        Product.objects.filter(_recommendable_product_q()).values_list("product_id", flat=True)
    )
    if not candidate_ids:
        return []

    artifacts = load_recommender_artifacts()
    if artifacts is None or not artifacts.get("product_ids"):
        fallback_ids = _fallback_popular_product_ids(candidate_ids, limit)
        return [{"product_id": int(pid), "score": 0.0, "reason": "Popular with shoppers"} for pid in fallback_ids]

    actor_key = _to_actor_key(user_id=user.id if user is not None else None, session_key=session_key)
    exclude_ids = _runtime_purchased_ids(user=user, session_key=session_key)

    recommendations = _recommend_from_artifacts(
        actor_key=actor_key,
        artifacts=artifacts,
        candidate_ids=candidate_ids,
        limit=limit,
        exclude_ids=exclude_ids,
    )
    if recommendations:
        if len(recommendations) < limit:
            existing_ids = {item["product_id"] for item in recommendations}
            fallback_ids = _fallback_popular_product_ids(candidate_ids, limit)
            for product_id in fallback_ids:
                if product_id in existing_ids or product_id in exclude_ids:
                    continue
                recommendations.append(
                    {
                        "product_id": int(product_id),
                        "score": 0.0,
                        "reason": "Popular with shoppers",
                    }
                )
                if len(recommendations) >= limit:
                    break
        return recommendations

    fallback_ids = _fallback_popular_product_ids(candidate_ids, limit)
    return [{"product_id": int(pid), "score": 0.0, "reason": "Popular with shoppers"} for pid in fallback_ids]


def get_recommendations(
    user: Optional[User] = None,
    session_key: Optional[str] = None,
    limit: int = DEFAULT_TOP_K,
) -> List[Product]:
    scored = recommend_with_scores(user=user, session_key=session_key, limit=limit)
    if not scored:
        return []

    product_ids = [item["product_id"] for item in scored]
    products = Product.objects.filter(
        product_id__in=product_ids,
    ).filter(
        _recommendable_product_q()
    ).select_related("category")
    product_map = {product.product_id: product for product in products}
    return [product_map[pid] for pid in product_ids if pid in product_map]


def _evaluate_predictions(
    relevant_by_actor: Dict[str, set[int]],
    prediction_lists: Dict[str, List[int]],
    candidate_count: int,
    k: int,
    known_train_actors: set[str],
) -> Dict[str, float]:
    if not relevant_by_actor:
        return {
            "actors_evaluated": 0,
            f"precision@{k}": 0.0,
            f"recall@{k}": 0.0,
            f"ndcg@{k}": 0.0,
            "coverage": 0.0,
            "cold_start_coverage": 0.0,
        }

    precision_sum = 0.0
    recall_sum = 0.0
    ndcg_sum = 0.0
    recommended_items: set[int] = set()

    cold_start_total = 0
    cold_start_with_recs = 0

    for actor_key, relevant_items in relevant_by_actor.items():
        predicted = prediction_lists.get(actor_key, [])[:k]
        predicted_set = set(predicted)
        recommended_items.update(predicted)

        hits = len(relevant_items.intersection(predicted_set))
        precision_sum += hits / float(k)
        recall_sum += hits / float(max(len(relevant_items), 1))

        dcg = 0.0
        for rank, product_id in enumerate(predicted):
            if product_id in relevant_items:
                dcg += 1.0 / np.log2(rank + 2)
        ideal_hits = min(len(relevant_items), k)
        idcg = sum(1.0 / np.log2(rank + 2) for rank in range(ideal_hits))
        ndcg_sum += (dcg / idcg) if idcg > 0 else 0.0

        if actor_key not in known_train_actors:
            cold_start_total += 1
            if predicted:
                cold_start_with_recs += 1

    actor_count = len(relevant_by_actor)
    coverage = len(recommended_items) / float(candidate_count) if candidate_count else 0.0
    cold_start_coverage = cold_start_with_recs / float(cold_start_total) if cold_start_total else 0.0

    return {
        "actors_evaluated": actor_count,
        f"precision@{k}": round(precision_sum / actor_count, 6),
        f"recall@{k}": round(recall_sum / actor_count, 6),
        f"ndcg@{k}": round(ndcg_sum / actor_count, 6),
        "coverage": round(coverage, 6),
        "cold_start_coverage": round(cold_start_coverage, 6),
    }


def _build_eval_predictions(
    split_df: pd.DataFrame,
    artifacts: Dict[str, object],
    candidate_ids: List[int],
    k: int,
) -> Tuple[Dict[str, List[int]], Dict[str, List[int]], Dict[str, set[int]]]:
    if split_df.empty:
        return {}, {}, {}

    relevant_by_actor = {
        actor_key: set(group["product_id"].astype(int).tolist())
        for actor_key, group in split_df.groupby("actor_key")
    }

    actor_history = artifacts.get("profiles", {}).get("actor_product_weights", {})
    popularity_ranking = sorted(
        candidate_ids,
        key=lambda pid: (-_safe_float(artifacts.get("popularity_scores", {}).get(pid, 0.0)), int(pid)),
    )

    model_predictions: Dict[str, List[int]] = {}
    baseline_predictions: Dict[str, List[int]] = {}

    for actor_key in relevant_by_actor.keys():
        history_ids = set(actor_history.get(actor_key, {}).keys())
        model_recs = _recommend_from_artifacts(
            actor_key=actor_key,
            artifacts=artifacts,
            candidate_ids=candidate_ids,
            limit=k,
            exclude_ids=history_ids,
        )
        model_predictions[actor_key] = [item["product_id"] for item in model_recs][:k]
        baseline_predictions[actor_key] = [pid for pid in popularity_ranking if pid not in history_ids][:k]

    return model_predictions, baseline_predictions, relevant_by_actor


def train_recommender_artifacts(
    top_k: int = DEFAULT_TOP_K,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
) -> Dict[str, object]:
    top_k = _normalize_limit(top_k)
    if train_ratio <= 0 or train_ratio >= 1:
        raise ValueError("train_ratio must be between 0 and 1")
    if val_ratio < 0 or val_ratio >= 1:
        raise ValueError("val_ratio must be between 0 and 1")
    if train_ratio + val_ratio >= 1:
        raise ValueError("train_ratio + val_ratio must be less than 1")

    product_frame = _build_product_frame()
    product_ids = [int(pid) for pid in product_frame["product_id"].tolist()]
    interactions_df = _build_interaction_frame(set(product_ids))

    split = temporal_split_interactions(interactions_df, train_ratio=train_ratio, val_ratio=val_ratio)
    train_df = split["train"]
    validation_df = split["validation"]
    test_df = split["test"]

    profiles = _build_training_profiles(train_df, product_frame)
    popularity_scores = _build_popularity_scores(train_df)

    vectorizer = None
    product_matrix = None
    item_similarity = None
    if not product_frame.empty:
        vectorizer, product_matrix = _build_content_artifacts(product_frame)
        item_similarity = _build_collaborative_artifacts(train_df, product_ids)

    payload = _prepare_artifact_payload(
        product_frame=product_frame,
        profiles=profiles,
        popularity_scores=popularity_scores,
        vectorizer=vectorizer,
        product_matrix=product_matrix,
        item_similarity=item_similarity,
        split_meta=split["meta"],
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        top_k=top_k,
    )

    eval_artifacts = {
        "product_ids": product_ids,
        "product_index": {pid: idx for idx, pid in enumerate(product_ids)},
        "product_category_map": {
            int(row.product_id): int(row.category_id) if pd.notna(row.category_id) else None
            for row in product_frame.itertuples()
        },
        "profiles": profiles,
        "popularity_scores": popularity_scores,
        "product_matrix": product_matrix,
        "item_similarity": item_similarity,
    }

    known_train_actors = set(profiles.get("actor_product_weights", {}).keys())
    val_model_preds, val_baseline_preds, val_relevant = _build_eval_predictions(
        split_df=validation_df,
        artifacts=eval_artifacts,
        candidate_ids=product_ids,
        k=top_k,
    )
    test_model_preds, test_baseline_preds, test_relevant = _build_eval_predictions(
        split_df=test_df,
        artifacts=eval_artifacts,
        candidate_ids=product_ids,
        k=top_k,
    )

    validation_metrics_model = _evaluate_predictions(
        relevant_by_actor=val_relevant,
        prediction_lists=val_model_preds,
        candidate_count=len(product_ids),
        k=top_k,
        known_train_actors=known_train_actors,
    )
    validation_metrics_baseline = _evaluate_predictions(
        relevant_by_actor=val_relevant,
        prediction_lists=val_baseline_preds,
        candidate_count=len(product_ids),
        k=top_k,
        known_train_actors=known_train_actors,
    )
    test_metrics_model = _evaluate_predictions(
        relevant_by_actor=test_relevant,
        prediction_lists=test_model_preds,
        candidate_count=len(product_ids),
        k=top_k,
        known_train_actors=known_train_actors,
    )
    test_metrics_baseline = _evaluate_predictions(
        relevant_by_actor=test_relevant,
        prediction_lists=test_baseline_preds,
        candidate_count=len(product_ids),
        k=top_k,
        known_train_actors=known_train_actors,
    )

    precision_key = f"precision@{top_k}"
    recall_key = f"recall@{top_k}"
    ndcg_key = f"ndcg@{top_k}"

    metrics = {
        "trained_at": payload["trained_at"],
        "data": {
            "products_count": int(len(product_frame)),
            "interactions_count": int(len(interactions_df)),
            "train_count": int(len(train_df)),
            "validation_count": int(len(validation_df)),
            "test_count": int(len(test_df)),
            "distinct_actors": int(interactions_df["actor_key"].nunique()) if not interactions_df.empty else 0,
        },
        "model": {"validation": validation_metrics_model, "test": test_metrics_model},
        "baseline": {"validation": validation_metrics_baseline, "test": test_metrics_baseline},
        "comparison": {
            "validation_precision_lift": round(
                validation_metrics_model.get(precision_key, 0.0) - validation_metrics_baseline.get(precision_key, 0.0),
                6,
            ),
            "validation_recall_lift": round(
                validation_metrics_model.get(recall_key, 0.0) - validation_metrics_baseline.get(recall_key, 0.0),
                6,
            ),
            "validation_ndcg_lift": round(
                validation_metrics_model.get(ndcg_key, 0.0) - validation_metrics_baseline.get(ndcg_key, 0.0),
                6,
            ),
            "test_precision_lift": round(
                test_metrics_model.get(precision_key, 0.0) - test_metrics_baseline.get(precision_key, 0.0),
                6,
            ),
            "test_recall_lift": round(
                test_metrics_model.get(recall_key, 0.0) - test_metrics_baseline.get(recall_key, 0.0),
                6,
            ),
            "test_ndcg_lift": round(
                test_metrics_model.get(ndcg_key, 0.0) - test_metrics_baseline.get(ndcg_key, 0.0),
                6,
            ),
        },
        "split": split["meta"],
        "top_k": top_k,
    }

    _save_artifacts(payload=payload, metrics=metrics)
    clear_artifact_cache()
    load_recommender_artifacts(force_reload=True)
    logger.info("Recommender training complete: products=%s interactions=%s", len(product_frame), len(interactions_df))
    return metrics


def get_quick_recommendations(user_id: int, n: int = 6) -> List[Product]:
    n = _normalize_limit(n)
    saved_recs = list(
        Recommendation.objects.filter(user_id=user_id)
        .select_related("product", "product__category")
        .order_by("-score")[:n]
    )
    saved_products = [
        rec.product
        for rec in saved_recs
        if rec.product and rec.product.is_available and (not rec.product.manages_local_stock or rec.product.stock_level > 0)
    ]
    if saved_products:
        return saved_products

    user = User.objects.filter(id=user_id).first()
    if user is None:
        return []
    return get_recommendations(user=user, limit=n)


def _persist_recommendation_rows(
    *,
    user: Optional[User] = None,
    session_key: Optional[str] = None,
    limit: int = DEFAULT_TOP_K,
) -> List[Recommendation]:
    scored = recommend_with_scores(user=user, session_key=session_key, limit=limit)
    if not scored:
        return []

    product_ids = [item["product_id"] for item in scored]
    products = Product.objects.filter(product_id__in=product_ids).filter(_recommendable_product_q())
    product_map = {product.product_id: product for product in products}

    rows: List[Recommendation] = []
    for item in scored:
        product = product_map.get(item["product_id"])
        if not product:
            continue
        rows.append(
            Recommendation(
                user=user,
                session_key=session_key,
                product=product,
                score=float(item["score"]),
                reason=item["reason"],
            )
        )

    if not rows:
        return []

    with transaction.atomic():
        if user is not None:
            Recommendation.objects.filter(user=user).delete()
        else:
            Recommendation.objects.filter(session_key=session_key).delete()
        Recommendation.objects.bulk_create(rows, ignore_conflicts=True)

    return rows


class RecommendationEngine:
    """Compatibility wrapper around artifact-backed recommendations."""

    def __init__(self):
        self.Product = Product
        self.Recommendation = Recommendation
        self.UserInteraction = UserInteraction

    def generate_recommendations_for_user(self, user_id: int, n: int = DEFAULT_TOP_K) -> List[Recommendation]:
        user = User.objects.filter(id=user_id).first()
        if user is None:
            return []
        return _persist_recommendation_rows(user=user, limit=n)

    def generate_recommendations_for_session(self, session_key: str, n: int = DEFAULT_TOP_K) -> List[Recommendation]:
        if not session_key:
            return []
        return _persist_recommendation_rows(session_key=session_key, limit=n)

    def generate_all_recommendations(self, n: int = DEFAULT_TOP_K, active_days: int = 90) -> int:
        since = timezone.now() - timedelta(days=max(1, int(active_days)))
        user_ids = list(
            UserInteraction.objects.filter(user__isnull=False, timestamp__gte=since)
            .values_list("user_id", flat=True)
            .distinct()
        )
        session_keys = list(
            UserInteraction.objects.filter(user__isnull=True, session_key__isnull=False, timestamp__gte=since)
            .values_list("session_key", flat=True)
            .distinct()
        )

        processed = 0
        for user_id in user_ids:
            if self.generate_recommendations_for_user(user_id=user_id, n=n):
                processed += 1
        for session_key in session_keys:
            if self.generate_recommendations_for_session(session_key=session_key, n=n):
                processed += 1
        return processed
