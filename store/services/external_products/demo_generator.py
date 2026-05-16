from __future__ import annotations

import random
from decimal import Decimal
from typing import Any

DEMO_GENERATED_SOURCE = 'demo_generated'

DEMO_CATEGORIES = [
    'Electronics',
    'Phones',
    'Laptops',
    'Cameras',
    'Fashion',
    'Shoes',
    'Watches',
    'Beauty',
    'Fragrances',
    'Furniture',
    'Groceries',
    'Kitchen Accessories',
    'Home Decoration',
    'Sports',
    'Toys',
    'Books',
    'Automotive',
    'Health',
    'Office Supplies',
    'Gaming',
]

TITLE_ADJECTIVES = [
    'Premium',
    'Smart',
    'Ultra',
    'Ergonomic',
    'Professional',
    'Compact',
    'Wireless',
    'Portable',
    'Modern',
    'Deluxe',
    'Pro',
    'Essential',
]

TITLE_NOUNS = [
    'Wireless Bluetooth Headphones',
    'Fitness Watch',
    'HD Action Camera',
    'Office Chair',
    'Kitchen Knife Set',
    'Wooden Coffee Table',
    'Running Shoes',
    'Leather Shoulder Bag',
    'Mechanical Keyboard',
    'Power Bank 20000mAh',
    'LED Desk Lamp',
    'Bluetooth Speaker',
    'Gaming Mouse',
    'Stainless Water Bottle',
    'Yoga Mat',
    'Backpack',
    'Tablet Stand',
    'Air Purifier',
    'Electric Kettle',
    'Smart Plug',
]

VARIANTS = [
    'Black',
    'White',
    'Silver',
    'Blue',
    'Red',
    'Large',
    'Medium',
    'Pro Model',
    '2024 Edition',
]


class DemoProductGenerator:
    """Generate unique local demo products when API catalogs are exhausted."""

    def __init__(self, *, seed: int | None = None):
        if seed is not None:
            random.seed(seed)

    def build_normalized_batch(
        self,
        count: int,
        *,
        start_index: int,
        existing_titles: set[str],
        existing_slugs: set[str],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        index = start_index
        attempts = 0
        max_attempts = count * 25

        while len(results) < count and attempts < max_attempts:
            attempts += 1
            normalized = self._build_one(index)
            index += 1
            title_key = normalized['title'].lower()
            slug_key = normalized.get('_slug_hint', '')
            if title_key in existing_titles:
                continue
            if slug_key and slug_key in existing_slugs:
                continue
            existing_titles.add(title_key)
            if slug_key:
                existing_slugs.add(slug_key)
            results.append(normalized)
        return results

    def _build_one(self, index: int) -> dict[str, Any]:
        category = random.choice(DEMO_CATEGORIES)
        adjective = random.choice(TITLE_ADJECTIVES)
        noun = random.choice(TITLE_NOUNS)
        variant = random.choice(VARIANTS)
        title = f'{adjective} {noun} ({variant}) #{index:04d}'
        external_id = f'demo-generated-{index:06d}'
        price = Decimal(str(random.randint(15, 899)))
        rating = Decimal(str(round(random.uniform(3.5, 5.0), 1)))
        stock = random.randint(20, 200)
        description = (
            f'{title} is a locally generated demo catalog item for storefront testing. '
            f'Category: {category}. Model ref {external_id}.'
        )
        image_seed = (index % 1000) + 1
        image_url = f'https://picsum.photos/seed/demo-{external_id}/{400}/{400}'

        return {
            'source': DEMO_GENERATED_SOURCE,
            'external_id': external_id,
            'title': title,
            'description': description,
            'category_name': category,
            'price': price,
            'currency': 'USD',
            'image_url': image_url,
            'rating': rating,
            'stock': stock,
            'availability': 'in_stock',
            'product_url': '',
            'raw_data': {
                'generated': True,
                'purpose': 'demo_fill',
                'source_label': 'demo_generated',
            },
            '_slug_hint': f'demo-generated-{external_id}',
        }
