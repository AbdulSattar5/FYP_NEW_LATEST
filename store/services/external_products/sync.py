from __future__ import annotations

import random
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from store.models import Category, ExternalProduct, ExternalSource, Product, ProductSyncLog
from store.utils.category_icons import icon_for_category_name
from store.utils.commerce import LOCAL_CHECKOUT_SOURCES, is_api_json_product_url

from .base import ExternalProviderError
from .bestbuy import BestBuyProvider
from .demo_generator import DEMO_GENERATED_SOURCE, DemoProductGenerator
from .dummyjson import DummyJsonProvider
from .platzi import PlatziProvider


@dataclass
class ExternalSyncSummary:
    source: str
    limit: int
    publish_enabled: bool
    target_count: int | None = None
    demo_fill_enabled: bool = False
    starting_product_count: int = 0
    missing_products_needed: int = 0
    fetched_count: int = 0
    normalized_count: int = 0
    created_external_count: int = 0
    updated_external_count: int = 0
    created_products_count: int = 0
    updated_products_count: int = 0
    demo_generated_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    final_product_count: int = 0
    final_category_count: int = 0
    status: str = 'success'
    log_id: int | None = None
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'source': self.source,
            'limit': self.limit,
            'publish_enabled': self.publish_enabled,
            'target_count': self.target_count,
            'demo_fill_enabled': self.demo_fill_enabled,
            'starting_product_count': self.starting_product_count,
            'missing_products_needed': self.missing_products_needed,
            'fetched_count': self.fetched_count,
            'normalized_count': self.normalized_count,
            'created_external_count': self.created_external_count,
            'updated_external_count': self.updated_external_count,
            'created_products_count': self.created_products_count,
            'updated_products_count': self.updated_products_count,
            'demo_generated_count': self.demo_generated_count,
            'skipped_count': self.skipped_count,
            'error_count': self.error_count,
            'final_product_count': self.final_product_count,
            'final_category_count': self.final_category_count,
            'status': self.status,
            'log_id': self.log_id,
            'errors': self.errors,
        }


class ExternalProductSyncService:
    SOURCE_ORDER = ('dummyjson', 'platzi', 'bestbuy')

    source_factories: dict[str, Callable[..., object]] = {
        'dummyjson': DummyJsonProvider,
        'platzi': PlatziProvider,
        'bestbuy': BestBuyProvider,
    }

    source_defaults: dict[str, dict[str, str]] = {
        'dummyjson': {'name': 'DummyJSON', 'base_url': 'https://dummyjson.com'},
        'platzi': {'name': 'Platzi Fake Store', 'base_url': 'https://api.escuelajs.co/api/v1'},
        'bestbuy': {'name': 'Best Buy', 'base_url': 'https://api.bestbuy.com/v1'},
        'demo_generated': {
            'name': 'Demo Generated (local)',
            'base_url': '',
        },
    }

    def _default_source_key(self) -> str:
        raw = getattr(settings, 'DEFAULT_PRODUCT_SOURCE', 'dummyjson')
        source_key = str(raw or 'dummyjson').strip().lower()
        return source_key if source_key in self.source_factories else 'dummyjson'

    def _build_provider(self, source_key: str):
        source_key = str(source_key).strip().lower()
        provider_cls = self.source_factories.get(source_key)
        if not provider_cls:
            raise ExternalProviderError(f'Unknown source "{source_key}"')
        api_key = ''
        if source_key == 'bestbuy':
            api_key = getattr(settings, 'BESTBUY_API_KEY', '')
        return provider_cls(api_key=api_key)

    def _upsert_source(self, source_key: str) -> ExternalSource:
        defaults = self.source_defaults.get(source_key, {'name': source_key.title(), 'base_url': ''})
        source_obj, _ = ExternalSource.objects.get_or_create(
            key=source_key,
            defaults=defaults,
        )
        changed = False
        if source_obj.name != defaults['name']:
            source_obj.name = defaults['name']
            changed = True
        if defaults.get('base_url') and source_obj.base_url != defaults['base_url']:
            source_obj.base_url = defaults['base_url']
            changed = True
        if changed:
            source_obj.save(update_fields=['name', 'base_url', 'updated_at'])
        return source_obj

    def _build_product_slug(self, title: str, source_key: str, external_id: str) -> str:
        base = slugify(f'{title}-{source_key}-{external_id}') or slugify(f'{source_key}-{external_id}')
        return base[:200]

    def _unique_product_slug(self, base_slug: str) -> str:
        slug = base_slug[:200] or 'product'
        if not Product.objects.filter(slug=slug).exists():
            return slug
        counter = 2
        while Product.objects.filter(slug=f'{slug}-{counter}'[:200]).exists():
            counter += 1
        return f'{slug}-{counter}'[:200]

    def _get_or_create_category(self, category_name: str) -> Category:
        clean_name = str(category_name or '').strip() or 'Uncategorized'
        base_slug = slugify(clean_name) or 'uncategorized'
        icon_class = icon_for_category_name(clean_name)

        category = Category.objects.filter(slug=base_slug).first()
        if category is None:
            category = Category.objects.filter(name__iexact=clean_name).first()

        if category is not None:
            if not category.icon or category.icon in {'fa-tag', 'fa-th'}:
                category.icon = icon_class
                category.save(update_fields=['icon'])
            return category

        slug = base_slug[:100]
        counter = 2
        while Category.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'[:100]
            counter += 1

        return Category.objects.create(
            name=clean_name,
            slug=slug,
            description=f'Products in {clean_name}',
            icon=icon_class,
        )

    def _resolve_stock_level(self, stock: int | None, source_key: str) -> int:
        level = max(0, int(stock or 0))
        if level > 0:
            return level
        if source_key in LOCAL_CHECKOUT_SOURCES:
            return random.randint(20, 200)
        return 0

    def _load_dedup_sets(self) -> tuple[set[str], set[str], set[str]]:
        titles = {name.lower() for name in Product.objects.values_list('name', flat=True) if name}
        slugs = set(Product.objects.values_list('slug', flat=True))
        external_keys = {
            f'{src}:{eid}'
            for src, eid in ExternalProduct.objects.values_list('source__key', 'external_id')
        }
        return titles, slugs, external_keys

    def _repair_local_demo_stock(self) -> int:
        repaired = 0
        products = Product.objects.filter(is_available=True, stock_level__lte=0)
        for product in products.iterator():
            attrs = product.attributes if isinstance(product.attributes, dict) else {}
            source_key = str(attrs.get('external_source') or '').lower()
            if source_key in LOCAL_CHECKOUT_SOURCES or attrs.get('generated'):
                product.stock_level = random.randint(20, 200)
                product.manages_local_stock = True
                product.external_url = ''
                product.is_available = True
                product.save(
                    update_fields=['stock_level', 'manages_local_stock', 'external_url', 'is_available', 'updated_at']
                )
                repaired += 1
        return repaired

    def _publish_to_product(self, external_product: ExternalProduct) -> tuple[Product, bool]:
        payload = {
            'title': external_product.title,
            'description': external_product.description,
            'category_name': external_product.category_name,
            'price': external_product.price or Decimal('0.00'),
            'currency': external_product.currency or 'USD',
            'image_url': external_product.image_url or '',
            'rating': external_product.rating or Decimal('0.0'),
            'stock': external_product.stock or 0,
            'availability': external_product.availability or '',
            'product_url': external_product.product_url or '',
        }

        category = self._get_or_create_category(payload['category_name'])
        source_key = external_product.source.key
        base_slug = self._build_product_slug(
            payload['title'],
            source_key,
            external_product.external_id,
        )

        product = external_product.published_product
        if product is None:
            product = Product.objects.filter(slug=base_slug).first()
        created = product is None
        if created:
            product = Product(slug=self._unique_product_slug(base_slug))

        product.name = payload['title'] or f'{external_product.source.name} Product'
        product.category = category
        product.description = payload['description'] or product.name
        product.price = payload['price'] if payload['price'] is not None else Decimal('0.00')
        product.original_price = None
        product.is_on_discount = False
        product.discount_percentage = Decimal('0.00')
        product.stock_level = self._resolve_stock_level(int(payload['stock'] or 0), source_key)
        product.is_available = True
        product.is_featured = product.is_featured if not created else False
        product.rating = payload['rating'] if payload['rating'] is not None else Decimal('0.0')

        raw_product_url = str(payload['product_url'] or '').strip()
        is_local_checkout = source_key in LOCAL_CHECKOUT_SOURCES

        if is_local_checkout:
            product.is_external = source_key != DEMO_GENERATED_SOURCE
            product.manages_local_stock = True
            product.external_url = ''
        else:
            product.is_external = True
            product.manages_local_stock = False
            product.external_url = (
                raw_product_url if raw_product_url and not is_api_json_product_url(raw_product_url) else ''
            )

        attributes = dict(product.attributes or {})
        attributes.update(
            {
                'external_source': source_key,
                'external_source_name': external_product.source.name,
                'external_id': external_product.external_id,
                'external_currency': payload['currency'],
                'external_image_url': payload['image_url'],
                'external_product_url': raw_product_url,
                'external_availability': payload['availability'],
                'local_checkout': is_local_checkout,
                'generated': bool(
                    isinstance(external_product.raw_data, dict)
                    and external_product.raw_data.get('generated')
                ),
            }
        )
        product.attributes = attributes
        product.save()

        external_product.published_product = product
        external_product.is_published = True
        external_product.save(update_fields=['published_product', 'is_published', 'updated_at', 'last_synced_at'])
        return product, created

    def _process_normalized(
        self,
        normalized: dict,
        *,
        source_obj: ExternalSource,
        publish: bool,
        titles: set[str],
        slugs: set[str],
        external_keys: set[str],
        summary: ExternalSyncSummary,
    ) -> bool:
        """Returns True if a new Product row was created (when publish=True)."""
        external_id = str(normalized.get('external_id') or '').strip()
        title = str(normalized.get('title') or '').strip()
        if not external_id or not title:
            summary.skipped_count += 1
            return False

        dedupe_key = f'{source_obj.key}:{external_id}'
        title_key = title.lower()
        slug_hint = normalized.get('_slug_hint') or self._build_product_slug(
            title, source_obj.key, external_id
        )

        try:
            external_product, ext_created = ExternalProduct.objects.update_or_create(
                source=source_obj,
                external_id=external_id,
                defaults={
                    'title': title,
                    'description': normalized.get('description', ''),
                    'category_name': normalized.get('category_name', 'Uncategorized'),
                    'price': normalized.get('price', Decimal('0.00')),
                    'currency': normalized.get('currency', 'USD'),
                    'image_url': normalized.get('image_url', ''),
                    'rating': normalized.get('rating', Decimal('0.0')),
                    'stock': normalized.get('stock', 0),
                    'availability': normalized.get('availability', ''),
                    'product_url': normalized.get('product_url', ''),
                    'raw_data': normalized.get('raw_data', {}),
                },
            )
            external_keys.add(dedupe_key)
            titles.add(title_key)
            slugs.add(slug_hint)

            if ext_created:
                summary.created_external_count += 1
            else:
                summary.updated_external_count += 1

            if not publish:
                return False

            _, product_created = self._publish_to_product(external_product)
            if product_created:
                summary.created_products_count += 1
            else:
                summary.updated_products_count += 1
            return product_created
        except Exception as exc:
            summary.error_count += 1
            summary.errors.append(str(exc))
            return False

    def _sources_for_run(self, source: str) -> list[str]:
        source_key = str(source or self._default_source_key()).strip().lower()
        if source_key == 'all':
            keys = []
            for key in self.SOURCE_ORDER:
                if key == 'bestbuy' and not getattr(settings, 'BESTBUY_API_KEY', ''):
                    continue
                keys.append(key)
            return keys
        return [source_key]

    def _fetch_from_provider(
        self,
        source_key: str,
        *,
        max_items: int,
        start_skip: int,
    ) -> list[dict]:
        provider = self._build_provider(source_key)
        if hasattr(provider, 'fetch_products_up_to'):
            return provider.fetch_products_up_to(max_items, start_skip=start_skip)
        return provider.fetch_products(max_items, skip=start_skip)

    def sync_to_target(
        self,
        *,
        source: str | None = None,
        target_count: int,
        publish: bool = False,
        demo_fill: bool = False,
        limit: int = 100,
        page: int | None = None,
        offset: int | None = None,
        skip: int | None = None,
    ) -> ExternalSyncSummary:
        source_label = str(source or 'all').strip().lower()
        starting_count = Product.objects.count()
        missing = max(0, int(target_count) - starting_count)

        summary = ExternalSyncSummary(
            source=source_label,
            limit=max(1, int(limit)),
            publish_enabled=bool(publish),
            target_count=int(target_count),
            demo_fill_enabled=bool(demo_fill),
            starting_product_count=starting_count,
            missing_products_needed=missing,
        )

        log_source = self._upsert_source(
            source_label if source_label != 'all' else self._default_source_key()
        )
        log = ProductSyncLog.objects.create(
            source=log_source,
            publish_enabled=bool(publish),
            status='success',
        )
        summary.log_id = log.id

        if missing <= 0:
            summary.final_product_count = starting_count
            summary.final_category_count = Category.objects.count()
            log.status = 'success'
            log.finished_at = timezone.now()
            log.summary = summary.to_dict()
            log.message = 'Target already reached.'
            log.save()
            return summary

        if publish:
            self._repair_local_demo_stock()

        titles, slugs, external_keys = self._load_dedup_sets()
        start_skip = int(skip if skip is not None else offset or 0)
        if page is not None and page > 1:
            start_skip = (int(page) - 1) * summary.limit

        products_created = 0

        per_source_skip = start_skip if source_label != 'all' else 0

        for source_key in self._sources_for_run(source_label):
            if products_created >= missing:
                break
            remaining = max(0, target_count - Product.objects.count())
            if remaining <= 0:
                break
            try:
                source_obj = self._upsert_source(source_key)
                fetch_cap = remaining
                normalized_batch = self._fetch_from_provider(
                    source_key,
                    max_items=fetch_cap,
                    start_skip=per_source_skip if source_label != 'all' else 0,
                )
                summary.fetched_count += len(normalized_batch)
                summary.normalized_count += len(normalized_batch)

                for normalized in normalized_batch:
                    if products_created >= missing:
                        break
                    if Product.objects.count() >= target_count:
                        break
                    created = self._process_normalized(
                        dict(normalized),
                        source_obj=source_obj,
                        publish=publish,
                        titles=titles,
                        slugs=slugs,
                        external_keys=external_keys,
                        summary=summary,
                    )
                    if created:
                        products_created += 1

                source_obj.last_synced_at = timezone.now()
                source_obj.save(update_fields=['last_synced_at', 'updated_at'])
            except ExternalProviderError as exc:
                summary.errors.append(str(exc))
            except Exception as exc:
                summary.error_count += 1
                summary.errors.append(f'{source_key}: {exc}')

        if demo_fill and publish:
            demo_source = self._upsert_source(DEMO_GENERATED_SOURCE)
            generator = DemoProductGenerator()
            demo_index = ExternalProduct.objects.filter(source=demo_source).count() + 1

            demo_iterations = 0
            max_demo_iterations = max(50, target_count // 5 + 10)

            while Product.objects.count() < target_count and demo_iterations < max_demo_iterations:
                demo_iterations += 1
                still_needed = target_count - Product.objects.count()
                batch = generator.build_normalized_batch(
                    still_needed,
                    start_index=demo_index,
                    existing_titles=titles,
                    existing_slugs=slugs,
                )
                if not batch:
                    summary.errors.append('Demo generator could not produce more unique products.')
                    break

                summary.fetched_count += len(batch)
                summary.normalized_count += len(batch)
                demo_index += len(batch)

                for normalized in batch:
                    if Product.objects.count() >= target_count:
                        break
                    created = self._process_normalized(
                        dict(normalized),
                        source_obj=demo_source,
                        publish=True,
                        titles=titles,
                        slugs=slugs,
                        external_keys=external_keys,
                        summary=summary,
                    )
                    if created:
                        summary.demo_generated_count += 1
                        products_created += 1

        summary.final_product_count = Product.objects.count()
        summary.final_category_count = Category.objects.count()

        if summary.error_count > 0 or summary.skipped_count > 0:
            summary.status = 'partial' if summary.error_count == 0 else 'partial'
        if summary.error_count > 0 and summary.created_products_count == 0 and summary.demo_generated_count == 0:
            summary.status = 'failed'

        log.status = summary.status
        log.finished_at = timezone.now()
        log.fetched_count = summary.fetched_count
        log.normalized_count = summary.normalized_count
        log.created_external_count = summary.created_external_count
        log.updated_external_count = summary.updated_external_count
        log.created_products_count = summary.created_products_count
        log.updated_products_count = summary.updated_products_count
        log.skipped_count = summary.skipped_count
        log.error_count = summary.error_count
        log.summary = summary.to_dict()
        log.message = '; '.join(summary.errors[:10])
        log.save()

        return summary

    def sync(
        self,
        *,
        source: str | None = None,
        limit: int = 100,
        publish: bool = False,
        target_count: int | None = None,
        demo_fill: bool = False,
        page: int | None = None,
        offset: int | None = None,
        skip: int | None = None,
    ) -> ExternalSyncSummary:
        if target_count is not None and int(target_count) > 0:
            return self.sync_to_target(
                source=source,
                target_count=int(target_count),
                publish=publish,
                demo_fill=demo_fill,
                limit=limit,
                page=page,
                offset=offset,
                skip=skip,
            )

        source_key = str(source or self._default_source_key()).strip().lower()
        if source_key == 'all':
            return self.sync_to_target(
                source='all',
                target_count=Product.objects.count() + max(1, int(limit)),
                publish=publish,
                demo_fill=demo_fill,
                limit=limit,
                page=page,
                offset=offset,
                skip=skip,
            )

        provider = self._build_provider(source_key)
        source_obj = self._upsert_source(source_key)

        summary = ExternalSyncSummary(
            source=source_key,
            limit=max(1, int(limit)),
            publish_enabled=bool(publish),
            starting_product_count=Product.objects.count(),
        )

        log = ProductSyncLog.objects.create(
            source=source_obj,
            publish_enabled=bool(publish),
            status='success',
        )
        summary.log_id = log.id

        start_skip = int(skip if skip is not None else offset or 0)
        if page is not None and page > 1:
            start_skip = (int(page) - 1) * summary.limit

        try:
            if publish:
                self._repair_local_demo_stock()

            titles, slugs, external_keys = self._load_dedup_sets()
            normalized_products = provider.fetch_products(summary.limit, skip=start_skip)
            summary.fetched_count = len(normalized_products)
            summary.normalized_count = len(normalized_products)

            for normalized in normalized_products:
                self._process_normalized(
                    dict(normalized),
                    source_obj=source_obj,
                    publish=publish,
                    titles=titles,
                    slugs=slugs,
                    external_keys=external_keys,
                    summary=summary,
                )

            source_obj.last_synced_at = timezone.now()
            source_obj.save(update_fields=['last_synced_at', 'updated_at'])
        except Exception as exc:
            summary.status = 'failed'
            summary.error_count += 1
            summary.errors.append(str(exc))

        if summary.status != 'failed':
            summary.status = 'partial' if (summary.error_count > 0 or summary.skipped_count > 0) else 'success'

        summary.final_product_count = Product.objects.count()
        summary.final_category_count = Category.objects.count()

        log.status = summary.status
        log.finished_at = timezone.now()
        log.fetched_count = summary.fetched_count
        log.normalized_count = summary.normalized_count
        log.created_external_count = summary.created_external_count
        log.updated_external_count = summary.updated_external_count
        log.created_products_count = summary.created_products_count
        log.updated_products_count = summary.updated_products_count
        log.skipped_count = summary.skipped_count
        log.error_count = summary.error_count
        log.summary = summary.to_dict()
        log.message = '; '.join(summary.errors[:10])
        log.save()

        return summary
