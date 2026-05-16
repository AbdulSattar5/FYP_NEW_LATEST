from __future__ import annotations

from typing import Any

from .base import BaseExternalProductProvider, ExternalProviderError


class DummyJsonProvider(BaseExternalProductProvider):
    source_key = 'dummyjson'
    source_name = 'DummyJSON'
    base_url = 'https://dummyjson.com'

    def fetch_raw_products(self, limit: int, *, skip: int = 0) -> list[dict[str, Any]]:
        return self._fetch_page(limit=max(1, int(limit)), skip=max(0, int(skip)))

    def fetch_raw_products_up_to(
        self,
        max_items: int,
        *,
        start_skip: int = 0,
        page_size: int = 100,
    ) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        skip = max(0, int(start_skip))
        page_size = min(100, max(1, int(page_size)))

        while len(collected) < max_items:
            limit = min(page_size, max_items - len(collected))
            endpoint = f'{self.base_url}/products'
            payload = self._get_json(endpoint, params={'limit': limit, 'skip': skip})
            if not isinstance(payload, dict):
                break
            batch = payload.get('products', [])
            if not isinstance(batch, list) or not batch:
                break
            batch = [item for item in batch if isinstance(item, dict)]
            collected.extend(batch)
            skip += len(batch)
            total = int(payload.get('total') or 0)
            if total and skip >= total:
                break
            if len(batch) < limit:
                break
        return collected[:max_items]

    def _fetch_page(self, *, limit: int, skip: int) -> list[dict[str, Any]]:
        endpoint = f'{self.base_url}/products'
        payload = self._get_json(endpoint, params={'limit': limit, 'skip': skip})
        if not isinstance(payload, dict):
            raise ExternalProviderError('dummyjson payload must be an object')
        products = payload.get('products', [])
        if not isinstance(products, list):
            raise ExternalProviderError('dummyjson payload missing products list')
        return [item for item in products if isinstance(item, dict)]

    def normalize_raw_product(self, raw_product: dict[str, Any]) -> dict[str, Any]:
        images = raw_product.get('images') if isinstance(raw_product.get('images'), list) else []
        image_url = raw_product.get('thumbnail') or (images[0] if images else '')
        category_name = raw_product.get('category') or 'Uncategorized'
        product_id = raw_product.get('id')
        return {
            'source': self.source_key,
            'external_id': str(product_id) if product_id is not None else '',
            'title': raw_product.get('title') or '',
            'description': raw_product.get('description') or '',
            'category_name': category_name,
            'price': raw_product.get('price'),
            'currency': 'USD',
            'image_url': image_url or '',
            'rating': raw_product.get('rating'),
            'stock': raw_product.get('stock'),
            'availability': 'in_stock' if int(raw_product.get('stock') or 0) > 0 else 'unknown',
            'product_url': '',
            'raw_data': raw_product,
        }
