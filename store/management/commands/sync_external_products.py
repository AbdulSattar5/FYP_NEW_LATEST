from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from store.models import Category, Product
from store.services.external_products.sync import ExternalProductSyncService


def _parse_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or '').strip().lower()
    return text in {'1', 'true', 'yes', 'y', 'on'}


class Command(BaseCommand):
    help = 'Sync products from external providers into local database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            default=getattr(settings, 'DEFAULT_PRODUCT_SOURCE', 'dummyjson'),
            help='Provider: dummyjson, platzi, bestbuy, all (default from DEFAULT_PRODUCT_SOURCE).',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Page size / max items per provider request (default: 100).',
        )
        parser.add_argument(
            '--target-count',
            type=int,
            default=None,
            help='Fill Product table until this many rows exist (e.g. 1000).',
        )
        parser.add_argument(
            '--publish',
            default='false',
            help='Publish synced products into Product table (true/false).',
        )
        parser.add_argument(
            '--demo-fill',
            default='false',
            help='Generate local demo products when APIs are exhausted (true/false).',
        )
        parser.add_argument(
            '--page',
            type=int,
            default=None,
            help='1-based page number (uses limit as page size for skip offset).',
        )
        parser.add_argument(
            '--offset',
            type=int,
            default=None,
            help='Skip offset for provider pagination.',
        )
        parser.add_argument(
            '--skip',
            type=int,
            default=None,
            help='Alias for --offset.',
        )

    def handle(self, *args, **options):
        source = str(options['source']).strip().lower()
        limit = max(1, int(options['limit']))
        publish = _parse_bool(options.get('publish'))
        demo_fill = _parse_bool(options.get('demo_fill'))
        target_count = options.get('target_count')
        page = options.get('page')
        offset = options.get('offset')
        skip = options.get('skip')

        valid_sources = {'dummyjson', 'platzi', 'bestbuy', 'all'}
        if source not in valid_sources:
            raise CommandError(f'Invalid --source "{source}". Choose: {", ".join(sorted(valid_sources))}')

        service = ExternalProductSyncService()
        try:
            summary = service.sync(
                source=source,
                limit=limit,
                publish=publish,
                target_count=int(target_count) if target_count is not None else None,
                demo_fill=demo_fill,
                page=page,
                offset=offset,
                skip=skip,
            )
        except Exception as exc:
            raise CommandError(f'External sync failed: {exc}') from exc

        if summary.target_count and summary.missing_products_needed <= 0:
            self.stdout.write(self.style.SUCCESS('Target already reached.'))
            self.stdout.write(f'Target count: {summary.target_count}')
            self.stdout.write(f'Starting product count: {summary.starting_product_count}')
            self.stdout.write(f'Final product count: {summary.final_product_count or Product.objects.count()}')
            self.stdout.write(f'Categories: {summary.final_category_count or Category.objects.count()}')
            return

        style = self.style.SUCCESS if summary.status == 'success' else self.style.WARNING
        self.stdout.write(style(f'External sync completed with status: {summary.status}'))

        if summary.target_count:
            self.stdout.write(f'Target count: {summary.target_count}')
            self.stdout.write(f'Starting product count: {summary.starting_product_count}')
            self.stdout.write(f'Missing products needed: {summary.missing_products_needed}')

        self.stdout.write(f'Source: {summary.source}')
        self.stdout.write(f'Limit (page size): {summary.limit}')
        self.stdout.write(f'Publish enabled: {summary.publish_enabled}')
        self.stdout.write(f'Demo fill enabled: {summary.demo_fill_enabled}')
        self.stdout.write(f'External products fetched: {summary.fetched_count}')
        self.stdout.write(f'Normalized products: {summary.normalized_count}')
        self.stdout.write(f'External products created: {summary.created_external_count}')
        self.stdout.write(f'External products updated: {summary.updated_external_count}')
        self.stdout.write(f'Products published (created): {summary.created_products_count}')
        self.stdout.write(f'Products published (updated): {summary.updated_products_count}')
        self.stdout.write(f'Demo generated products: {summary.demo_generated_count}')
        self.stdout.write(f'Skipped: {summary.skipped_count}')
        self.stdout.write(f'Errors: {summary.error_count}')
        self.stdout.write(f'Final product count: {summary.final_product_count or Product.objects.count()}')
        self.stdout.write(f'Final categories count: {summary.final_category_count or Category.objects.count()}')

        if summary.log_id:
            self.stdout.write(f'Sync log ID: {summary.log_id}')

        if summary.errors:
            self.stdout.write(self.style.WARNING('Error details:'))
            for message in summary.errors[:10]:
                self.stdout.write(f'- {message}')
