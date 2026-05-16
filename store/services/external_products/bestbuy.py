from __future__ import annotations

from typing import Any

from .base import BaseExternalProductProvider, ExternalProviderError


class BestBuyProvider(BaseExternalProductProvider):
    source_key = 'bestbuy'
    source_name = 'Best Buy'
    base_url = 'https://api.bestbuy.com/v1'

    def fetch_raw_products(self, limit: int, *, skip: int = 0) -> list[dict[str, Any]]:
        if not self.api_key:
            raise ExternalProviderError('BESTBUY_API_KEY is required for Best Buy provider')

        endpoint = f'{self.base_url}/products((salePrice>0))'
        params = {
            'apiKey': self.api_key,
            'format': 'json',
            'pageSize': limit,
            'show': 'sku,name,salePrice,shortDescription,longDescription,image,url,customerReviewAverage,categoryPath,onlineAvailability',
        }
        payload = self._get_json(endpoint, params=params)
        if not isinstance(payload, dict):
            raise ExternalProviderError('bestbuy payload must be an object')
        products = payload.get('products', [])
        if not isinstance(products, list):
            raise ExternalProviderError('bestbuy payload missing products list')
        return [item for item in products if isinstance(item, dict)]

    def normalize_raw_product(self, raw_product: dict[str, Any]) -> dict[str, Any]:
        category_path = raw_product.get('categoryPath') if isinstance(raw_product.get('categoryPath'), list) else []
        category_name = 'Uncategorized'
        if category_path:
            last = category_path[-1]
            if isinstance(last, dict):
                category_name = last.get('name') or category_name

        sku = raw_product.get('sku')
        description = raw_product.get('longDescription') or raw_product.get('shortDescription') or ''
        return {
            'source': self.source_key,
            'external_id': str(sku) if sku is not None else '',
            'title': raw_product.get('name') or '',
            'description': description,
            'category_name': category_name,
            'price': raw_product.get('salePrice'),
            'currency': 'USD',
            'image_url': raw_product.get('image') or '',
            'rating': raw_product.get('customerReviewAverage') or 0,
            'stock': 0,
            'availability': 'in_stock' if bool(raw_product.get('onlineAvailability')) else 'unknown',
            'product_url': raw_product.get('url') or '',
            'raw_data': raw_product,
        }
