import shutil
from datetime import timedelta
from pathlib import Path
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from store.models import Category, Product, Recommendation, UserInteraction
import store.recommendation_engine as recommendation_engine
from store.recommendation_engine import (
    RecommendationEngine,
    clear_artifact_cache,
    get_recommendations,
    load_recommender_artifacts,
    train_recommender_artifacts,
)


class RecommenderPipelineTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Gadgets", slug="gadgets")
        self.product_a = Product.objects.create(
            name="Phone A",
            slug="phone-a",
            category=self.category,
            description="A budget phone",
            price=100,
            stock_level=10,
            rating=4.2,
            is_available=True,
        )
        self.product_b = Product.objects.create(
            name="Phone B",
            slug="phone-b",
            category=self.category,
            description="A mid-range phone",
            price=150,
            stock_level=8,
            rating=4.4,
            is_available=True,
        )
        self.product_c = Product.objects.create(
            name="Phone C",
            slug="phone-c",
            category=self.category,
            description="A premium phone",
            price=220,
            stock_level=6,
            rating=4.8,
            is_available=True,
        )
        self.out_of_stock_product = Product.objects.create(
            name="Sold Out Phone",
            slug="sold-out-phone",
            category=self.category,
            description="Out of stock product",
            price=180,
            stock_level=0,
            rating=4.9,
            is_available=True,
        )
        self.user = User.objects.create_user(username="rec_user", password="Password123!")
        self.other_user = User.objects.create_user(username="other_user", password="Password123!")
        self.cold_user = User.objects.create_user(username="cold_user", password="Password123!")

        self.original_artifact_relative_dir = recommendation_engine.ARTIFACT_RELATIVE_DIR
        self.test_artifact_relative_dir = Path("models") / f"recommender_test_{uuid.uuid4().hex}"
        recommendation_engine.ARTIFACT_RELATIVE_DIR = self.test_artifact_relative_dir

        self.artifact_dir = Path(settings.BASE_DIR) / self.test_artifact_relative_dir
        if self.artifact_dir.exists():
            shutil.rmtree(self.artifact_dir, ignore_errors=True)
        clear_artifact_cache()

    def tearDown(self):
        recommendation_engine.ARTIFACT_RELATIVE_DIR = self.original_artifact_relative_dir
        if self.artifact_dir.exists():
            shutil.rmtree(self.artifact_dir, ignore_errors=True)
        clear_artifact_cache()

    def _create_interaction(self, *, user=None, session_key=None, product=None, interaction_type="view", when=None):
        if when is None:
            when = timezone.now()
        interaction = UserInteraction.objects.create(
            user=user,
            session_key=session_key,
            product=product,
            interaction_type=interaction_type,
            interaction_count=1,
        )
        UserInteraction.objects.filter(pk=interaction.pk).update(timestamp=when)
        interaction.refresh_from_db()
        return interaction

    def _seed_interactions(self):
        base = timezone.now() - timedelta(days=5)
        self._create_interaction(user=self.user, product=self.product_a, interaction_type="view", when=base)
        self._create_interaction(user=self.user, product=self.product_b, interaction_type="cart", when=base + timedelta(hours=1))
        self._create_interaction(user=self.other_user, product=self.product_b, interaction_type="view", when=base + timedelta(hours=2))
        self._create_interaction(user=self.other_user, product=self.product_c, interaction_type="purchase", when=base + timedelta(hours=3))
        self._create_interaction(session_key="anon-1", product=self.product_a, interaction_type="click", when=base + timedelta(hours=4))
        self._create_interaction(session_key="anon-1", product=self.product_c, interaction_type="view", when=base + timedelta(hours=5))

    def test_empty_products_returns_empty_recommendations(self):
        Product.objects.all().delete()
        UserInteraction.objects.all().delete()
        train_recommender_artifacts(top_k=5)

        recs = get_recommendations(user=self.user, limit=5)
        self.assertEqual(recs, [])

    def test_empty_interactions_uses_fallback(self):
        UserInteraction.objects.all().delete()
        train_recommender_artifacts(top_k=3)

        recs = get_recommendations(user=self.user, limit=3)
        self.assertGreater(len(recs), 0)
        self.assertLessEqual(len(recs), 3)

    def test_cold_start_user_gets_recommendations(self):
        self._seed_interactions()
        train_recommender_artifacts(top_k=4)

        recs = get_recommendations(user=self.cold_user, limit=4)
        self.assertGreater(len(recs), 0)
        self.assertLessEqual(len(recs), 4)

    def test_out_of_stock_products_are_excluded(self):
        base = timezone.now() - timedelta(days=3)
        self._create_interaction(user=self.user, product=self.out_of_stock_product, interaction_type="purchase", when=base)
        self._create_interaction(user=self.user, product=self.product_a, interaction_type="view", when=base + timedelta(hours=1))
        self._create_interaction(user=self.other_user, product=self.out_of_stock_product, interaction_type="view", when=base + timedelta(hours=2))

        train_recommender_artifacts(top_k=5)
        rec_ids = [product.product_id for product in get_recommendations(user=self.user, limit=5)]
        self.assertNotIn(self.out_of_stock_product.product_id, rec_ids)

    def test_temporal_split_prevents_future_leakage_in_train_profiles(self):
        base = timezone.now() - timedelta(days=2)
        self._create_interaction(user=self.user, product=self.product_a, interaction_type="view", when=base)
        self._create_interaction(user=self.other_user, product=self.product_b, interaction_type="view", when=base + timedelta(minutes=10))
        self._create_interaction(user=self.user, product=self.product_c, interaction_type="purchase", when=base + timedelta(minutes=20))
        self._create_interaction(user=self.other_user, product=self.product_a, interaction_type="cart", when=base + timedelta(minutes=30))

        train_recommender_artifacts(top_k=3, train_ratio=0.5, val_ratio=0.25)
        artifacts = load_recommender_artifacts(force_reload=True)

        actor_key = f"u:{self.user.id}"
        trained_history = artifacts["profiles"]["actor_product_weights"].get(actor_key, {})
        self.assertIn(self.product_a.product_id, trained_history)
        self.assertNotIn(self.product_c.product_id, trained_history)

    def test_artifact_loading_after_training(self):
        self._seed_interactions()
        metrics = train_recommender_artifacts(top_k=3)

        self.assertTrue((self.artifact_dir / "config.json").exists())
        self.assertTrue((self.artifact_dir / "metrics.json").exists())
        self.assertIn("model", metrics)
        artifacts = load_recommender_artifacts(force_reload=True)
        self.assertIsNotNone(artifacts)
        self.assertIn("product_ids", artifacts)

    def test_recommendation_count_respects_limit(self):
        self._seed_interactions()
        train_recommender_artifacts(top_k=6)

        recs = get_recommendations(user=self.user, limit=2)
        self.assertLessEqual(len(recs), 2)

    def test_generate_recommendations_does_not_duplicate_rows(self):
        self._seed_interactions()
        train_recommender_artifacts(top_k=5)

        engine = RecommendationEngine()
        first = engine.generate_recommendations_for_user(user_id=self.user.id, n=5)
        second = engine.generate_recommendations_for_user(user_id=self.user.id, n=5)

        self.assertGreaterEqual(len(first), 0)
        self.assertGreaterEqual(len(second), 0)

        rows = Recommendation.objects.filter(user=self.user)
        self.assertEqual(rows.count(), rows.values("product_id").distinct().count())
