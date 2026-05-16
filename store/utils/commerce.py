from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

# Demo APIs and locally generated catalog — no real storefront; never use as "Buy on Source".
DEMO_API_SOURCES = frozenset({'dummyjson', 'platzi'})
LOCAL_CHECKOUT_SOURCES = frozenset({'dummyjson', 'platzi', 'demo_generated'})

# Host/path patterns that return JSON API payloads, not product pages.
_API_JSON_URL_PATTERNS = (
    re.compile(r'^https?://(www\.)?dummyjson\.com/products(/\d+)?/?$', re.I),
    re.compile(r'^https?://api\.escuelajs\.co/api/v1/products(/\d+)?/?$', re.I),
    re.compile(r'^https?://api\.bestbuy\.com/', re.I),
)


def external_source_key_from_attributes(attributes: Any) -> str:
    if not isinstance(attributes, dict):
        return ''
    return str(attributes.get('external_source') or '').strip().lower()


def is_demo_api_source(source_key: str) -> bool:
    return (source_key or '').lower() in DEMO_API_SOURCES


def is_local_checkout_source(source_key: str) -> bool:
    return (source_key or '').lower() in LOCAL_CHECKOUT_SOURCES


def is_api_json_product_url(url: str) -> bool:
    """True when URL is an API endpoint that returns JSON, not a storefront page."""
    cleaned = (url or '').strip()
    if not cleaned:
        return False
    for pattern in _API_JSON_URL_PATTERNS:
        if pattern.match(cleaned):
            return True
    parsed = urlparse(cleaned)
    path = (parsed.path or '').lower()
    if path.endswith('.json'):
        return True
    if '/api/v1/products' in path or '/api/v1/product' in path:
        return True
    return False


def resolve_buy_on_source_url(
    external_url: str,
    attributes: dict[str, Any] | None = None,
) -> str:
    """
    Return a safe affiliate/storefront URL, or empty string if checkout must stay local.
    """
    attrs = attributes if isinstance(attributes, dict) else {}
    source_key = external_source_key_from_attributes(attrs)

    if is_local_checkout_source(source_key):
        return ''

    for candidate in (external_url, attrs.get('external_product_url'), attrs.get('product_url')):
        url = str(candidate or '').strip()
        if not url:
            continue
        if is_api_json_product_url(url):
            continue
        if urlparse(url).scheme in ('http', 'https'):
            return url
    return ''
