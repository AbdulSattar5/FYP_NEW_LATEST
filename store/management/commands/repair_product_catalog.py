from __future__ import annotations

import random

from django.core.management.base import BaseCommand
from django.db.models import Q

from store.models import Category, Product
from store.utils.category_icons import icon_for_category_name
from store.utils.commerce import (
    LOCAL_CHECKOUT_SOURCES,
    external_source_key_from_attributes,
    is_api_json_product_url,
    resolve_buy_on_source_url,
)


class Command(BaseCommand):
    help = (
        'Repair legacy catalog rows: local checkout for demo APIs, remove JSON API URLs, '
        'restore stock, and refresh category icons.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--feature-top',
            type=int,
            default=8,
            help='Mark this many top-rated products as featured when none are featured (0 to skip).',
        )

    def handle(self, *args, **options):
        feature_top = max(0, int(options['feature_top']))
        products_fixed = 0
        attrs_urls_cleared = 0
        stock_fixed = 0

        for product in Product.objects.iterator():
            attrs = dict(product.attributes) if isinstance(product.attributes, dict) else {}
            source_key = external_source_key_from_attributes(attrs)
            update_fields: list[str] = []
            local_checkout = source_key in LOCAL_CHECKOUT_SOURCES or bool(attrs.get('generated'))

            if local_checkout:
                if not product.manages_local_stock:
                    product.manages_local_stock = True
                    update_fields.append('manages_local_stock')
                if product.external_url:
                    product.external_url = ''
                    update_fields.append('external_url')
            elif product.external_url and is_api_json_product_url(product.external_url):
                safe = resolve_buy_on_source_url(product.external_url, attrs)
                product.external_url = safe
                update_fields.append('external_url')

            attrs_changed = False
            for key in ('external_product_url', 'product_url'):
                url = str(attrs.get(key) or '').strip()
                if url and is_api_json_product_url(url):
                    attrs[key] = ''
                    attrs_changed = True
                    attrs_urls_cleared += 1

            if local_checkout and attrs.get('local_checkout') is not True:
                attrs['local_checkout'] = True
                attrs_changed = True

            if attrs_changed:
                product.attributes = attrs
                update_fields.append('attributes')

            if local_checkout and product.is_available and product.stock_level <= 0:
                product.stock_level = random.randint(20, 200)
                update_fields.append('stock_level')
                stock_fixed += 1

            if not product.is_available and local_checkout:
                product.is_available = True
                update_fields.append('is_available')

            if update_fields:
                update_fields.append('updated_at')
                product.save(update_fields=list(dict.fromkeys(update_fields)))
                products_fixed += 1

        icons_updated = 0
        for category in Category.objects.iterator():
            icon = icon_for_category_name(category.name)
            if category.icon != icon:
                category.icon = icon
                category.save(update_fields=['icon'])
                icons_updated += 1

        featured_set = 0
        if feature_top and not Product.objects.filter(is_featured=True).exists():
            top_ids = list(
                Product.objects.filter(is_available=True, stock_level__gt=0)
                .order_by('-rating', '-product_id')
                .values_list('product_id', flat=True)[:feature_top]
            )
            if top_ids:
                featured_set = Product.objects.filter(product_id__in=top_ids).update(is_featured=True)

        total = Product.objects.count()
        bad_external = Product.objects.filter(
            Q(external_url__icontains='dummyjson.com/products')
            | Q(external_url__icontains='api.escuelajs.co/api/v1/products')
        ).count()
        zero_stock = Product.objects.filter(is_available=True, stock_level__lte=0).count()

        self.stdout.write(self.style.SUCCESS('Catalog repair complete.'))
        self.stdout.write(f'  Products updated: {products_fixed}')
        self.stdout.write(f'  Attribute API URLs cleared: {attrs_urls_cleared}')
        self.stdout.write(f'  Stock restored (local checkout): {stock_fixed}')
        self.stdout.write(f'  Category icons refreshed: {icons_updated}')
        self.stdout.write(f'  Featured products set: {featured_set}')
        self.stdout.write(f'  Total products: {total}')
        self.stdout.write(f'  Remaining bad external_url: {bad_external}')
        self.stdout.write(f'  Remaining zero-stock available: {zero_stock}')
