from __future__ import annotations

import csv
import hashlib
import logging
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from django.conf import settings
from store.models import Category, Product

logger = logging.getLogger(__name__)


@dataclass
class ImportSummary:
    source_file: str = ""
    total_rows: int = 0
    created_products: int = 0
    updated_products: int = 0
    created_categories: int = 0
    skipped_rows: int = 0
    errors: int = 0
    messages: list[str] = field(default_factory=list)


class ProductImporter:
    """
    Import products from the real CSV files bundled with the project.
    """

    CATEGORY_CONFIG = {
        "Electronics": {"icon": "fa-laptop", "color": "#6C63FF"},
        "Phones": {"icon": "fa-mobile-alt", "color": "#3F8EFC"},
        "Laptops": {"icon": "fa-laptop", "color": "#6C63FF"},
        "Clothing": {"icon": "fa-tshirt", "color": "#FF6584"},
        "Books": {"icon": "fa-book", "color": "#43AA8B"},
        "Food": {"icon": "fa-utensils", "color": "#F8961E"},
        "Home & Kitchen": {"icon": "fa-home", "color": "#9B59B6"},
        "Sports": {"icon": "fa-football-ball", "color": "#E74C3C"},
        "Toys": {"icon": "fa-gamepad", "color": "#F39C12"},
        "Beauty": {"icon": "fa-spa", "color": "#E91E63"},
        "Hi-Fi Speakers": {"icon": "fa-volume-up", "color": "#00BCD4"},
        "Other Electronics": {"icon": "fa-plug", "color": "#607D8B"},
        "General": {"icon": "fa-tag", "color": "#95A5A6"},
    }

    SOURCE_FILES = {
        "cleaned": "amazon_products_sales_data_cleaned.csv",
        "products": "amazon_products.csv",
        "uk": "amz_uk_processed_data.csv",
        "categories": "amazon_categories.csv",
    }

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = Path(base_dir or settings.BASE_DIR)
        self.category_cache: dict[str, Category] = {}
        self.uk_category_lookup: dict[str, str] = {}

    def import_products(self, source: str = "auto", clear: bool = False, limit: int | None = None) -> ImportSummary:
        summary = ImportSummary()

        if clear:
            Product.objects.all().delete()

        source_path, source_name = self.resolve_source(source)
        summary.source_file = str(source_path.name)

        if source_name == "uk":
            self.uk_category_lookup = self.load_uk_category_lookup()

        if source_name == "cleaned":
            self.import_cleaned_csv(source_path, summary, limit)
        elif source_name == "products":
            self.import_products_csv(source_path, summary, limit)
        elif source_name == "uk":
            self.import_uk_csv(source_path, summary, limit)
        else:
            raise FileNotFoundError("No valid product CSV found in the project.")

        return summary

    def resolve_source(self, source: str) -> tuple[Path, str]:
        if source != "auto":
            filename = self.SOURCE_FILES[source]
            path = self.base_dir / filename
            if not path.exists():
                raise FileNotFoundError(f"CSV file not found: {filename}")
            return path, source

        for source_name in ("cleaned", "products", "uk"):
            path = self.base_dir / self.SOURCE_FILES[source_name]
            if path.exists() and self._file_has_expected_headers(path, source_name):
                return path, source_name

        raise FileNotFoundError("No valid product CSV found in the project.")

    def _file_has_expected_headers(self, path: Path, source_name: str) -> bool:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = {header.strip() for header in (reader.fieldnames or [])}

        expected = {
            "cleaned": {"product_title", "product_category"},
            "products": {"title", "product_name", "price"},
            "uk": {"asin", "title", "price"},
        }
        return bool(headers & expected[source_name])

    def load_uk_category_lookup(self) -> dict[str, str]:
        categories_path = self.base_dir / self.SOURCE_FILES["categories"]
        if not categories_path.exists():
            return {}

        lookup: dict[str, str] = {}
        with categories_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                category_id = self.first_non_empty(row, ["id", "category_id"])
                category_name = self.first_non_empty(row, ["category_name", "name"])
                if category_id and category_name:
                    lookup[str(category_id).strip()] = category_name.strip()
        return lookup

    def import_cleaned_csv(self, path: Path, summary: ImportSummary, limit: int | None) -> None:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row_number, row in enumerate(reader, start=2):
                if limit is not None and summary.total_rows >= limit:
                    break
                self._import_cleaned_row(row, row_number, summary, path.name)

    def import_products_csv(self, path: Path, summary: ImportSummary, limit: int | None) -> None:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row_number, row in enumerate(reader, start=2):
                if limit is not None and summary.total_rows >= limit:
                    break
                self._import_generic_row(row, row_number, summary, path.name, source_label="products")

    def import_uk_csv(self, path: Path, summary: ImportSummary, limit: int | None) -> None:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row_number, row in enumerate(reader, start=2):
                if limit is not None and summary.total_rows >= limit:
                    break
                self._import_generic_row(row, row_number, summary, path.name, source_label="uk")

    def _import_cleaned_row(self, row: dict[str, Any], row_number: int, summary: ImportSummary, source_file: str) -> None:
        summary.total_rows += 1

        try:
            name = self.first_non_empty(row, ["product_title", "title", "name"])
            if not name:
                summary.skipped_rows += 1
                return

            category_name = self.first_non_empty(row, ["product_category", "category", "category_name"]) or "General"
            price = self.parse_decimal(self.first_non_empty(row, ["discounted_price", "price", "original_price", "listPrice"]))
            original_price = self.parse_decimal(self.first_non_empty(row, ["original_price", "listPrice", "price"]))
            if price is None and original_price is not None:
                price = original_price
            if price is None or price <= 0:
                summary.skipped_rows += 1
                return

            rating = self.parse_decimal(self.first_non_empty(row, ["product_rating", "stars", "rating"]))
            reviews = self.parse_int(self.first_non_empty(row, ["total_reviews", "reviews"]))
            stock_level = self.parse_int(self.first_non_empty(row, ["stock_level", "stock", "inventory", "purchased_last_month"]))
            if stock_level is None or stock_level <= 0:
                stock_level = 10

            category = self.get_or_create_category(category_name, summary)
            source_key = self.make_source_key(source_file, self.first_non_empty(row, ["product_page_url", "productURL", "product_url", "asin"]) or name)
            description = self.build_description(name, rating, reviews, row)
            is_best_seller = self.parse_bool(self.first_non_empty(row, ["is_best_seller", "isBestSeller"]))
            discount_percentage = self.parse_decimal(self.first_non_empty(row, ["discount_percentage", "discount_pct"]))
            is_on_discount = bool(discount_percentage and discount_percentage > 0)
            image = None

            attributes = self.build_attributes(
                row,
                source_file=source_file,
                source_key=source_key,
                source_label="cleaned",
                extra={
                    "source_url": self.first_non_empty(row, ["product_page_url"]),
                    "image_url": self.first_non_empty(row, ["product_image_url"]),
                    "reviews": reviews,
                    "purchased_last_month": self.parse_int(self.first_non_empty(row, ["purchased_last_month"])),
                    "is_sponsored": self.first_non_empty(row, ["is_sponsored"]),
                    "has_coupon": self.first_non_empty(row, ["has_coupon"]),
                    "buy_box_availability": self.first_non_empty(row, ["buy_box_availability"]),
                    "delivery_date": self.first_non_empty(row, ["delivery_date"]),
                    "sustainability_tags": self.first_non_empty(row, ["sustainability_tags"]),
                },
            )

            self.upsert_product(
                summary=summary,
                source_key=source_key,
                category=category,
                name=name,
                description=description,
                price=price,
                original_price=original_price if original_price and original_price > price else None,
                is_on_discount=is_on_discount,
                discount_percentage=discount_percentage or Decimal("0"),
                stock_level=stock_level,
                is_available=True,
                is_featured=is_best_seller,
                rating=rating or Decimal("0"),
                image=image,
                attributes=attributes,
            )
        except Exception:
            summary.errors += 1
            summary.skipped_rows += 1
            logger.exception("Failed to import row %s from %s", row_number, source_file)

    def _import_generic_row(
        self,
        row: dict[str, Any],
        row_number: int,
        summary: ImportSummary,
        source_file: str,
        source_label: str,
    ) -> None:
        summary.total_rows += 1

        try:
            if source_label == "uk":
                name = self.first_non_empty(row, ["title", "product_title", "name"])
                category_id = self.first_non_empty(row, ["category_id", "category"])
                category_name = self.uk_category_lookup.get(str(category_id or ""), "General")
                if category_name == "General":
                    raw_category = self.first_non_empty(row, ["categoryName", "category_name"])
                    if raw_category:
                        category_name = raw_category
                source_ref = self.first_non_empty(row, ["asin", "productURL", "product_url", "title"])
                price = self.parse_decimal(self.first_non_empty(row, ["price", "listPrice", "original_price"]))
                original_price = self.parse_decimal(self.first_non_empty(row, ["listPrice", "original_price", "price"]))
                rating = self.parse_decimal(self.first_non_empty(row, ["stars", "rating"]))
                reviews = self.parse_int(self.first_non_empty(row, ["reviews", "total_reviews"]))
                stock_level = self.parse_int(self.first_non_empty(row, ["stock", "stock_level", "boughtInLastMonth"]))
                if stock_level is None or stock_level <= 0:
                    stock_level = 10
                is_best_seller = self.parse_bool(self.first_non_empty(row, ["isBestSeller", "is_best_seller"]))
                image = None
            else:
                name = self.first_non_empty(row, ["product_name", "title", "name"])
                category_name = self.first_non_empty(row, ["category", "category_name", "product_category"]) or "General"
                source_ref = self.first_non_empty(row, ["productURL", "product_page_url", "asin", "url", "sku", "name"])
                price = self.parse_decimal(self.first_non_empty(row, ["price", "listPrice", "original_price", "discounted_price"]))
                original_price = self.parse_decimal(self.first_non_empty(row, ["listPrice", "original_price", "price"]))
                rating = self.parse_decimal(self.first_non_empty(row, ["rating", "stars", "product_rating"]))
                reviews = self.parse_int(self.first_non_empty(row, ["reviews", "total_reviews"]))
                stock_level = self.parse_int(self.first_non_empty(row, ["stock", "stock_level", "inventory", "quantity"]))
                if stock_level is None or stock_level <= 0:
                    stock_level = 10
                is_best_seller = self.parse_bool(self.first_non_empty(row, ["is_best_seller", "isBestSeller"]))
                image = None

            if not name:
                summary.skipped_rows += 1
                return

            if price is None or price <= 0:
                summary.skipped_rows += 1
                return

            category = self.get_or_create_category(category_name or "General", summary)
            source_key = self.make_source_key(source_file, source_ref or name)
            description = self.build_description(name, rating, reviews, row)
            discount_percentage = self.parse_decimal(self.first_non_empty(row, ["discount_percentage", "discount_pct"]))
            is_on_discount = bool(discount_percentage and discount_percentage > 0)

            attributes = self.build_attributes(
                row,
                source_file=source_file,
                source_key=source_key,
                source_label=source_label,
                extra={
                    "source_url": source_ref,
                    "image_url": self.first_non_empty(row, ["imgUrl", "image", "image_url", "product_image_url"]),
                    "reviews": reviews,
                    "bought_last_month": self.parse_int(self.first_non_empty(row, ["boughtInLastMonth", "purchased_last_month"])),
                    "is_best_seller": is_best_seller,
                },
            )

            self.upsert_product(
                summary=summary,
                source_key=source_key,
                category=category,
                name=name,
                description=description,
                price=price,
                original_price=original_price if original_price and original_price > price else None,
                is_on_discount=is_on_discount,
                discount_percentage=discount_percentage or Decimal("0"),
                stock_level=stock_level,
                is_available=True,
                is_featured=is_best_seller,
                rating=rating or Decimal("0"),
                image=image,
                attributes=attributes,
            )
        except Exception:
            summary.errors += 1
            summary.skipped_rows += 1
            logger.exception("Failed to import row %s from %s", row_number, source_file)

    def upsert_product(
        self,
        *,
        summary: ImportSummary,
        source_key: str,
        category: Category,
        name: str,
        description: str,
        price: Decimal,
        original_price: Decimal | None,
        is_on_discount: bool,
        discount_percentage: Decimal,
        stock_level: int,
        is_available: bool,
        is_featured: bool,
        rating: Decimal,
        image: Any,
        attributes: dict[str, Any],
    ) -> None:
        existing = Product.objects.filter(attributes__source_key=source_key).first()
        if existing is None:
            existing = Product.objects.filter(name=name, category=category).first()

        product_defaults = {
            "category": category,
            "description": description,
            "price": price,
            "original_price": original_price,
            "is_on_discount": is_on_discount,
            "discount_percentage": discount_percentage,
            "stock_level": stock_level,
            "is_available": is_available,
            "is_featured": is_featured,
            "rating": rating,
            "image": image,
            "attributes": attributes,
        }

        if existing:
            for key, value in product_defaults.items():
                setattr(existing, key, value)
            existing.save()
            summary.updated_products += 1
            return

        Product.objects.create(name=name, slug="", **product_defaults)
        summary.created_products += 1

    def get_or_create_category(self, category_name: str, summary: ImportSummary) -> Category:
        normalized = self.normalize_category_name(category_name)
        if normalized in self.category_cache:
            return self.category_cache[normalized]

        config = self.CATEGORY_CONFIG.get(normalized, self.CATEGORY_CONFIG["General"])
        category, created = Category.objects.get_or_create(
            name=normalized,
            defaults={
                "description": f"Browse our collection of {normalized}",
                "icon": config["icon"],
                "color": config["color"],
            },
        )
        if created:
            summary.created_categories += 1
        self.category_cache[normalized] = category
        return category

    def build_attributes(
        self,
        row: dict[str, Any],
        *,
        source_file: str,
        source_key: str,
        source_label: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        attributes: dict[str, Any] = {}
        existing = row.get("attributes")
        if isinstance(existing, dict):
            attributes.update(existing)

        attributes.update(
            {
                "source_key": source_key,
                "source_file": source_file,
                "source_label": source_label,
            }
        )
        if extra:
            for key, value in extra.items():
                if value not in ("", None):
                    attributes[key] = value
        return attributes

    def build_description(self, name: str, rating: Decimal | None, reviews: int | None, row: dict[str, Any]) -> str:
        parts = [name]
        if rating is not None:
            parts.append(f"Rating: {rating}/5")
        if reviews is not None:
            parts.append(f"Reviews: {reviews}")
        if row.get("product_category"):
            parts.append(f"Category: {row.get('product_category')}")
        return "\n".join(parts)

    def normalize_category_name(self, category_name: str) -> str:
        name = str(category_name or "General").strip()
        return name or "General"

    def make_source_key(self, source_file: str, raw_value: str) -> str:
        raw = str(raw_value or "").strip()
        if not raw:
            raw = source_file
        digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
        return f"{source_file}:{digest}"

    def first_non_empty(self, row: dict[str, Any], keys: list[str]) -> str | None:
        for key in keys:
            value = row.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return None

    def parse_decimal(self, value: Any) -> Decimal | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        cleaned = re.sub(r"[^0-9.\-]", "", text)
        if cleaned in {"", ".", "-", "-."}:
            return None
        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None

    def parse_int(self, value: Any) -> int | None:
        decimal_value = self.parse_decimal(value)
        if decimal_value is None:
            return None
        return int(decimal_value)

    def parse_bool(self, value: Any) -> bool:
        if value is None:
            return False
        text = str(value).strip().lower()
        return text in {"1", "true", "yes", "y", "best seller", "best seller badge", "best seller?"}
