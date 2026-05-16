from __future__ import annotations

from typing import Any

from .base import BaseExternalProductProvider, ExternalProviderError


class PlatziProvider(BaseExternalProductProvider):
    source_key = 'platzi'
    source_name = 'Platzi Fake Store'
    base_url = 'https://api.escuelajs.co/api/v1'

    def fetch_raw_products(self, limit: int, *, skip: int = 0) -> list[dict[str, Any]]:
        return self._fetch_page(limit=max(1, int(limit)), offset=max(0, int(skip)))

    def fetch_raw_products_up_to(
        self,
        max_items: int,
        *,
        start_skip: int = 0,
        page_size: int = 50,
    ) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        offset = max(0, int(start_skip))
        page_size = max(1, min(50, int(page_size)))

        while len(collected) < max_items:
            batch = self._fetch_page(limit=min(page_size, max_items - len(collected)), offset=offset)
            if not batch:
                break
            collected.extend(batch)
            offset += len(batch)
            if len(batch) < page_size:
                break
        return collected[:max_items]

    def _fetch_page(self, *, limit: int, offset: int) -> list[dict[str, Any]]:
        endpoint = f'{self.base_url}/products'
        payload = self._get_json(endpoint, params={'offset': offset, 'limit': limit})
        if not isinstance(payload, list):
            raise ExternalProviderError('platzi payload must be a list')
        return [item for item in payload if isinstance(item, dict)]

    def normalize_raw_product(self, raw_product: dict[str, Any]) -> dict[str, Any]:
        category = raw_product.get('category') if isinstance(raw_product.get('category'), dict) else {}
        images = raw_product.get('images') if isinstance(raw_product.get('images'), list) else []
        product_id = raw_product.get('id')
        return {
            'source': self.source_key,
            'external_id': str(product_id) if product_id is not None else '',
            'title': raw_product.get('title') or '',
            'description': raw_product.get('description') or '',
            'category_name': category.get('name') or 'Uncategorized',
            'price': raw_product.get('price'),
            'currency': 'USD',
            'image_url': images[0] if images else '',
            'rating': 0,
            'stock': raw_product.get('stock') or 0,
            'availability': 'unknown',
            'product_url': '',
            'raw_data': raw_product,
        }
