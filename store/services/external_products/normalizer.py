from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


def _clean_text(value: Any, default: str = '') -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _clean_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
    if value in (None, ''):
        return default
    try:
        return Decimal(str(value)).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError):
        return default


def _clean_int(value: Any, default: int = 0) -> int:
    if value in (None, ''):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clean_rating(value: Any, default: Decimal = Decimal('0.0')) -> Decimal:
    raw = _clean_decimal(value, default=default)
    if raw < 0:
        return Decimal('0.0')
    if raw > 5:
        return Decimal('5.0')
    return raw.quantize(Decimal('0.1'))


def normalize_external_product(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Final normalization gate for every provider payload.
    Required output format:
    {
      "source": "dummyjson",
      "external_id": "...",
      "title": "...",
      "description": "...",
      "category_name": "...",
      "price": 0,
      "currency": "USD",
      "image_url": "...",
      "rating": 0,
      "stock": 0,
      "availability": "...",
      "product_url": "...",
      "raw_data": {}
    }
    """
    raw_data = payload.get('raw_data') if isinstance(payload.get('raw_data'), dict) else {}
    normalized = {
        'source': _clean_text(payload.get('source')),
        'external_id': _clean_text(payload.get('external_id')),
        'title': _clean_text(payload.get('title')),
        'description': _clean_text(payload.get('description')),
        'category_name': _clean_text(payload.get('category_name'), default='Uncategorized'),
        'price': _clean_decimal(payload.get('price'), default=Decimal('0.00')),
        'currency': _clean_text(payload.get('currency'), default='USD'),
        'image_url': _clean_text(payload.get('image_url')),
        'rating': _clean_rating(payload.get('rating')),
        'stock': max(0, _clean_int(payload.get('stock'), default=0)),
        'availability': _clean_text(payload.get('availability')),
        'product_url': _clean_text(payload.get('product_url')),
        'raw_data': raw_data,
    }
    return normalized
