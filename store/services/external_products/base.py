from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import requests

from .normalizer import normalize_external_product


class ExternalProviderError(Exception):
    """Raised when a provider request/response is invalid."""


class BaseExternalProductProvider(ABC):
    source_key: str = ''
    source_name: str = ''
    base_url: str = ''
    default_timeout: int = 20

    def __init__(self, *, api_key: str = '', timeout: int | None = None):
        self.api_key = (api_key or '').strip()
        self.timeout = timeout or self.default_timeout
        self.session = requests.Session()

    @abstractmethod
    def fetch_raw_products(self, limit: int) -> list[dict[str, Any]]:
        """Fetch raw products from external source."""

    @abstractmethod
    def normalize_raw_product(self, raw_product: dict[str, Any]) -> dict[str, Any]:
        """Map raw provider payload into project normalized format."""

    def fetch_products(self, limit: int, *, skip: int = 0) -> list[dict[str, Any]]:
        raw_products = self.fetch_raw_products(limit=max(1, int(limit)), skip=skip)
        return self._normalize_batch(raw_products)

    def fetch_products_up_to(
        self,
        max_items: int,
        *,
        start_skip: int = 0,
        page_size: int = 100,
    ) -> list[dict[str, Any]]:
        if hasattr(self, 'fetch_raw_products_up_to'):
            raw_products = self.fetch_raw_products_up_to(
                max_items,
                start_skip=start_skip,
                page_size=page_size,
            )
        else:
            raw_products = self.fetch_raw_products(limit=max_items, skip=start_skip)
        return self._normalize_batch(raw_products)

    def _normalize_batch(self, raw_products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for raw in raw_products:
            normalized.append(
                normalize_external_product(self.normalize_raw_product(raw))
            )
        return normalized

    def _get_json(self, url: str, *, params: dict[str, Any] | None = None) -> dict[str, Any] | list[Any]:
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise ExternalProviderError(f'{self.source_key} request failed: {exc}') from exc
        except ValueError as exc:
            raise ExternalProviderError(f'{self.source_key} returned invalid JSON') from exc
