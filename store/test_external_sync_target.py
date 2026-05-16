import io
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from store.models import Category, ExternalProduct, Product
from store.services.external_products.sync import ExternalProductSyncService
from store.utils.commerce import is_api_json_product_url


class TargetCountSyncTests(TestCase):
    def test_target_count_argument_accepted(self):
        out = io.StringIO()
        call_command(
            'sync_external_products',
            '--target-count',
            '5',
            '--publish',
            'true',
            '--demo-fill',
            'true',
            stdout=out,
        )
        self.assertIn('Target count: 5', out.getvalue())

    def test_target_already_reached_creates_zero(self):
        category = Category.objects.create(name='Cat A', slug='cat-a')
        for index in range(5):
            Product.objects.create(
                name=f'Existing {index}',
                slug=f'existing-{index}',
                category=category,
                description='x',
                price=Decimal('10'),
                stock_level=25,
                is_available=True,
            )
        starting = Product.objects.count()
        out = io.StringIO()
        call_command(
            'sync_external_products',
            '--target-count',
            str(starting),
            '--publish',
            'true',
            '--demo-fill',
            'true',
            stdout=out,
        )
        self.assertEqual(Product.objects.count(), starting)
        self.assertIn('Target already reached', out.getvalue())

    @patch('store.services.external_products.base.requests.Session.get')
    def test_demo_fill_reaches_target_count(self, mock_get):
        mock_get.side_effect = self._mock_dummyjson_pages
        call_command(
            'sync_external_products',
            '--source',
            'dummyjson',
            '--target-count',
            '15',
            '--publish',
            'true',
            '--demo-fill',
            'true',
        )
        self.assertEqual(Product.objects.count(), 15)
        demo_count = Product.objects.filter(
            attributes__external_source='demo_generated'
        ).count()
        self.assertGreater(demo_count, 0)

    @patch('store.services.external_products.base.requests.Session.get')
    def test_demo_fill_false_stops_after_api_exhausted(self, mock_get):
        mock_get.side_effect = self._mock_dummyjson_pages
        call_command(
            'sync_external_products',
            '--source',
            'dummyjson',
            '--target-count',
            '500',
            '--publish',
            'true',
            '--demo-fill',
            'false',
        )
        self.assertLess(Product.objects.count(), 500)
        self.assertEqual(
            Product.objects.filter(attributes__external_source='demo_generated').count(),
            0,
        )

    @patch('store.services.external_products.base.requests.Session.get')
    def test_duplicate_sync_idempotent_for_target(self, mock_get):
        mock_get.side_effect = self._mock_dummyjson_pages
        call_command(
            'sync_external_products',
            '--source',
            'dummyjson',
            '--target-count',
            '12',
            '--publish',
            'true',
            '--demo-fill',
            'true',
        )
        first_count = Product.objects.count()
        call_command(
            'sync_external_products',
            '--source',
            'dummyjson',
            '--target-count',
            '12',
            '--publish',
            'true',
            '--demo-fill',
            'true',
        )
        self.assertEqual(Product.objects.count(), first_count)

    def test_category_slug_duplicate_does_not_crash(self):
        Category.objects.create(name='Electronics', slug='electronics')
        service = ExternalProductSyncService()
        cat = service._get_or_create_category('Electronics')
        self.assertEqual(cat.slug, 'electronics')
        cat2 = service._get_or_create_category('electronics')
        self.assertTrue(cat2.slug.startswith('electronics'))

    def _mock_dummyjson_pages(self, url, params=None, timeout=None, **kwargs):
        response = Mock()
        response.raise_for_status.return_value = None
        skip = int((params or {}).get('skip', 0))
        limit = int((params or {}).get('limit', 100))
        all_products = [
            {
                'id': index,
                'title': f'API Product {index}',
                'description': f'Desc {index}',
                'category': 'electronics',
                'price': 50 + index,
                'stock': 5,
                'rating': 4.2,
                'thumbnail': f'https://example.com/{index}.jpg',
                'images': [],
            }
            for index in range(1, 11)
        ]
        batch = all_products[skip : skip + limit]
        response.json.return_value = {
            'products': batch,
            'total': len(all_products),
            'skip': skip,
            'limit': limit,
        }
        return response


class GeneratedProductBehaviorTests(TestCase):
    def setUp(self):
        self._mock_patcher = patch('store.services.external_products.base.requests.Session.get')
        self._mock_get = self._mock_patcher.start()
        self._mock_get.side_effect = TargetCountSyncTests()._mock_dummyjson_pages
        call_command(
            'sync_external_products',
            '--target-count',
            '8',
            '--publish',
            'true',
            '--demo-fill',
            'true',
        )

    def tearDown(self):
        self._mock_patcher.stop()

    def test_generated_products_have_stock(self):
        self.assertTrue(Product.objects.filter(stock_level__gt=0).count() >= 8)

    def test_generated_products_no_buy_on_source(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertNotContains(response, 'Buy on Source')

    def test_search_finds_generated_product(self):
        product = Product.objects.filter(name__icontains='API Product').first()
        self.assertIsNotNone(product)
        response = self.client.get(reverse('store:search'), {'q': 'API Product'})
        self.assertContains(response, product.name)

    def test_add_to_cart_for_synced_product(self):
        User.objects.create_user(username='buyer1', password='Pass12345!')
        self.client.login(username='buyer1', password='Pass12345!')
        product = Product.objects.filter(stock_level__gt=0).first()
        self.assertTrue(product.can_add_to_cart)
        response = self.client.post(
            reverse('store:add_to_cart', args=[product.product_id]),
            data='{"quantity": 1}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

    def test_api_json_url_detection(self):
        self.assertTrue(is_api_json_product_url('https://dummyjson.com/products/44'))
