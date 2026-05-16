import json
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product
from store.utils.commerce import is_api_json_product_url, resolve_buy_on_source_url
from store.utils.category_icons import icon_for_category_slug


class CommerceUtilityTests(TestCase):
    def test_api_json_urls_are_detected(self):
        self.assertTrue(is_api_json_product_url('https://dummyjson.com/products/44'))
        self.assertTrue(is_api_json_product_url('https://api.escuelajs.co/api/v1/products/44'))
        self.assertFalse(is_api_json_product_url('https://www.bestbuy.com/site/product/123.p'))

    def test_demo_source_never_returns_buy_url(self):
        url = resolve_buy_on_source_url(
            'https://dummyjson.com/products/44',
            {'external_source': 'dummyjson'},
        )
        self.assertEqual(url, '')

    def test_valid_storefront_url_for_non_demo_source(self):
        url = resolve_buy_on_source_url(
            'https://www.bestbuy.com/site/product/123.p',
            {'external_source': 'bestbuy'},
        )
        self.assertEqual(url, 'https://www.bestbuy.com/site/product/123.p')

    def test_category_icon_mapper(self):
        self.assertEqual(icon_for_category_slug('beauty'), 'fa-spa')
        self.assertEqual(icon_for_category_slug('unknown-category'), 'fa-box')


class ProductButtonBehaviorTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Phones', slug='phones')
        self.local_product = Product.objects.create(
            name='Local Phone',
            slug='local-phone',
            category=self.category,
            description='Local stock',
            price=Decimal('100.00'),
            stock_level=5,
            is_available=True,
            manages_local_stock=True,
        )
        self.demo_imported = Product.objects.create(
            name='Demo Import',
            slug='demo-import',
            category=self.category,
            description='From DummyJSON',
            price=Decimal('50.00'),
            stock_level=8,
            is_available=True,
            is_external=True,
            manages_local_stock=True,
            external_url='',
            attributes={'external_source': 'dummyjson'},
        )
        self.legacy_demo = Product.objects.create(
            name='Legacy Demo',
            slug='legacy-demo',
            category=self.category,
            description='Old publish flags',
            price=Decimal('40.00'),
            stock_level=3,
            is_available=True,
            is_external=True,
            manages_local_stock=False,
            external_url='https://dummyjson.com/products/99',
            attributes={'external_source': 'dummyjson'},
        )
    def test_local_product_detail_shows_add_to_cart(self):
        response = self.client.get(
            reverse('store:product_detail', args=[self.local_product.product_id])
        )
        self.assertContains(response, 'Add to Cart')
        self.assertNotContains(response, 'Buy on Source')

    def test_demo_imported_product_uses_add_to_cart(self):
        self.assertTrue(self.demo_imported.can_add_to_cart)
        self.assertFalse(self.demo_imported.is_affiliate_product)
        response = self.client.get(
            reverse('store:product_detail', args=[self.demo_imported.product_id])
        )
        self.assertContains(response, 'Add to Cart')
        self.assertNotContains(response, 'Buy on Source')

    def test_legacy_demo_with_api_url_still_adds_to_cart(self):
        self.assertTrue(self.legacy_demo.can_add_to_cart)
        self.assertFalse(self.legacy_demo.is_affiliate_product)
        self.assertEqual(self.legacy_demo.buy_on_source_url, '')

    def test_add_to_cart_api_for_imported_product(self):
        User.objects.create_user(username='cart_user', password='CartPass123!')
        self.client.login(username='cart_user', password='CartPass123!')
        response = self.client.post(
            reverse('store:add_to_cart', args=[self.demo_imported.product_id]),
            data=json.dumps({'quantity': 1}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')


class AffiliateProductTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='TV', slug='tv-display')
        self.affiliate = Product.objects.create(
            name='Best Buy Item',
            slug='bestbuy-item',
            category=self.category,
            description='Affiliate',
            price=Decimal('200.00'),
            stock_level=0,
            is_available=True,
            is_external=True,
            manages_local_stock=False,
            external_url='https://www.bestbuy.com/site/product/abc.p',
            attributes={'external_source': 'bestbuy'},
        )

    def test_affiliate_with_valid_url_shows_buy_on_source(self):
        self.assertTrue(self.affiliate.is_affiliate_product)
        self.assertFalse(self.affiliate.can_add_to_cart)
        response = self.client.get(
            reverse('store:product_detail', args=[self.affiliate.product_id])
        )
        self.assertContains(response, 'Buy on Source')
        self.assertNotContains(response, 'dummyjson.com/products')
