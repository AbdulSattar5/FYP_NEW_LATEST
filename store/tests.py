import io
import json
import shutil
import tempfile
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

import store.recommendation_engine as recommendation_engine
from store.models import Category, ExternalProduct, Order, Product, UserInteraction
from store.product_importer import ProductImporter
from store.recommendation_engine import clear_artifact_cache, train_recommender_artifacts


class ApiEndpointsTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            name='Laptop Pro',
            slug='laptop-pro',
            category=self.category,
            description='Powerful laptop for creators',
            price=1000,
            stock_level=5,
            rating=4.5,
            is_available=True,
        )
        self.out_of_stock_product = Product.objects.create(
            name='Old Camera',
            slug='old-camera',
            category=self.category,
            description='Vintage camera',
            price=300,
            stock_level=0,
            rating=4.1,
            is_available=True,
        )
        self.inactive_product = Product.objects.create(
            name='Hidden Product',
            slug='hidden-product',
            category=self.category,
            description='Should not be returned in APIs',
            price=500,
            stock_level=10,
            rating=4.7,
            is_available=False,
        )

        self.user = User.objects.create_user(
            username='apitester',
            password='SecurePass123!',
            email='apitester@example.com',
        )

    def _json_post(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_search_suggestions_short_query_returns_empty(self):
        response = self.client.get(reverse('store:api_search_suggestions'), {'q': 'a'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['suggestions'], [])

    def test_search_suggestions_returns_matching_products(self):
        response = self.client.get(reverse('store:api_search_suggestions'), {'q': 'Laptop'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertLessEqual(len(data['suggestions']), 10)
        self.assertEqual(data['suggestions'][0]['id'], self.product.product_id)
        self.assertIn('title', data['suggestions'][0])

    def test_track_interaction_logged_in(self):
        self.client.login(username='apitester', password='SecurePass123!')
        response = self._json_post(reverse('store:track_interaction'), {
            'product_id': self.product.product_id,
            'interaction_type': 'view',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertTrue(
            UserInteraction.objects.filter(
                user=self.user,
                product=self.product,
                interaction_type='view',
            ).exists()
        )

    def test_track_interaction_anonymous_uses_session(self):
        response = self._json_post(reverse('store:track_interaction'), {
            'product_id': self.product.product_id,
            'interaction_type': 'click',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        session = self.client.session
        self.assertIn('anonymous_interactions', session)
        self.assertTrue(len(session['anonymous_interactions']) >= 1)

    def test_track_interaction_invalid_type(self):
        response = self._json_post(reverse('store:track_interaction'), {
            'product_id': self.product.product_id,
            'interaction_type': 'invalid',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_track_interaction_purchase_not_double_logged(self):
        self.client.login(username='apitester', password='SecurePass123!')
        response = self._json_post(reverse('store:track_interaction'), {
            'product_id': self.product.product_id,
            'interaction_type': 'purchase',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertFalse(
            UserInteraction.objects.filter(
                user=self.user,
                product=self.product,
                interaction_type='purchase',
            ).exists()
        )

    def test_cart_update_updates_quantity_and_totals(self):
        session = self.client.session
        session['cart'] = {
            str(self.product.product_id): {
                'name': self.product.name,
                'price': float(self.product.discount_price),
                'image': '',
                'quantity': 1,
                'product_id': self.product.product_id,
            }
        }
        session.save()

        response = self._json_post(
            reverse('store:cart_update', args=[self.product.product_id]),
            {'quantity': 2},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 2)
        expected_total = round(float(self.product.discount_price) * 2, 2)
        self.assertEqual(data['subtotal'], expected_total)
        self.assertEqual(data['total'], expected_total)

    def test_cart_update_quantity_zero_removes_item(self):
        session = self.client.session
        session['cart'] = {
            str(self.product.product_id): {
                'name': self.product.name,
                'price': float(self.product.discount_price),
                'image': '',
                'quantity': 1,
                'product_id': self.product.product_id,
            }
        }
        session.save()

        response = self._json_post(
            reverse('store:cart_update', args=[self.product.product_id]),
            {'quantity': 0},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['cart_count'], 0)
        self.assertNotIn(str(self.product.product_id), self.client.session.get('cart', {}))

    def test_cart_update_negative_quantity_rejected(self):
        response = self._json_post(
            reverse('store:cart_update', args=[self.product.product_id]),
            {'quantity': -1},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_cart_update_respects_stock(self):
        response = self._json_post(
            reverse('store:cart_update', args=[self.product.product_id]),
            {'quantity': 10},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_recommendations_api_filters_inactive_and_out_of_stock(self):
        response = self.client.get(reverse('store:api_recommendations'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        returned_ids = [item['id'] for item in data['recommendations']]
        self.assertIn(self.product.product_id, returned_ids)
        self.assertNotIn(self.out_of_stock_product.product_id, returned_ids)
        self.assertNotIn(self.inactive_product.product_id, returned_ids)

    def test_recommendations_api_returns_empty_when_no_products(self):
        Product.objects.all().delete()
        response = self.client.get(reverse('store:api_recommendations'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['recommendations'], [])

    def test_product_quick_view_api_success(self):
        response = self.client.get(
            reverse('store:api_product_quick_view', args=[self.product.product_id])
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['product']['id'], self.product.product_id)
        self.assertEqual(data['product']['title'], self.product.name)
        self.assertIn('description', data['product'])
        self.assertIn('stock', data['product'])

    def test_product_quick_view_api_404(self):
        response = self.client.get(reverse('store:api_product_quick_view', args=[999999]))

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Product not found')


class OrderPlacementSafetyTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Books', slug='books')
        self.product = Product.objects.create(
            name='Atomic Habits',
            slug='atomic-habits',
            category=self.category,
            description='Bestselling book',
            price=1000,
            stock_level=10,
            is_available=True,
        )
        self.user = User.objects.create_user(
            username='checkout_user',
            password='CheckoutPass123!',
        )
        self.client.login(username='checkout_user', password='CheckoutPass123!')

    def _seed_cart(self, quantity=1):
        session = self.client.session
        session['cart'] = {
            str(self.product.product_id): {
                'name': self.product.name,
                'price': float(self.product.discount_price),
                'image': '',
                'quantity': quantity,
                'product_id': self.product.product_id,
            }
        }
        session.save()

    def _get_submission_token(self):
        response = self.client.get(reverse('store:place_order', args=[self.product.product_id]))
        self.assertEqual(response.status_code, 200)
        token_key = f'order_submission_token_{self.product.product_id}'
        return self.client.session.get(token_key)

    def _place_order(self, quantity, token):
        return self.client.post(
            reverse('store:place_order', args=[self.product.product_id]),
            data={
                'quantity': quantity,
                'delivery_address': '123 Test Street',
                'city': 'Karachi',
                'phone_number': '03001234567',
                'notes': '',
                'submission_token': token,
            },
        )

    def test_stock_is_reduced_once_and_purchase_logged_once(self):
        self._seed_cart(quantity=2)
        token = self._get_submission_token()

        response = self._place_order(quantity=2, token=token)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store:order_history'))

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_level, 8)

        order = Order.objects.get()
        self.assertEqual(order.quantity, 2)

        interaction = UserInteraction.objects.get(
            user=self.user,
            product=self.product,
            interaction_type='purchase',
        )
        self.assertEqual(interaction.interaction_count, 1)

    def test_insufficient_stock_fails_and_cart_is_not_cleared(self):
        self.product.stock_level = 1
        self.product.save(update_fields=['stock_level'])
        self._seed_cart(quantity=2)
        token = self._get_submission_token()

        response = self._place_order(quantity=2, token=token)
        self.assertEqual(response.status_code, 200)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_level, 1)
        self.assertEqual(Order.objects.count(), 0)
        self.assertFalse(
            UserInteraction.objects.filter(
                user=self.user,
                product=self.product,
                interaction_type='purchase',
            ).exists()
        )
        self.assertIn(str(self.product.product_id), self.client.session.get('cart', {}))

    def test_cart_is_cleared_only_after_success(self):
        self._seed_cart(quantity=1)
        token = self._get_submission_token()

        response = self._place_order(quantity=1, token=token)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(str(self.product.product_id), self.client.session.get('cart', {}))

    def test_refresh_does_not_create_duplicate_order(self):
        self._seed_cart(quantity=2)
        token = self._get_submission_token()

        first_response = self._place_order(quantity=2, token=token)
        self.assertEqual(first_response.status_code, 302)
        self.assertRedirects(first_response, reverse('store:order_history'))

        second_response = self._place_order(quantity=2, token=token)
        self.assertEqual(second_response.status_code, 302)
        self.assertRedirects(second_response, reverse('store:order_history'))

        self.assertEqual(Order.objects.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_level, 8)
        interaction = UserInteraction.objects.get(
            user=self.user,
            product=self.product,
            interaction_type='purchase',
        )
        self.assertEqual(interaction.interaction_count, 1)

    def test_invalid_product_checkout_is_blocked(self):
        response = self.client.get(reverse('store:place_order', args=[999999]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('store:product_list'),
            fetch_redirect_response=False,
        )


class RecommendationViewIntegrationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Audio', slug='audio')
        self.product_1 = Product.objects.create(
            name='Headphones X',
            slug='headphones-x',
            category=self.category,
            description='Noise cancelling headphones',
            price=120,
            stock_level=6,
            rating=4.6,
            is_available=True,
        )
        self.product_2 = Product.objects.create(
            name='Speaker Mini',
            slug='speaker-mini',
            category=self.category,
            description='Portable speaker',
            price=80,
            stock_level=4,
            rating=4.3,
            is_available=True,
        )
        self.out_of_stock = Product.objects.create(
            name='Legacy Earbuds',
            slug='legacy-earbuds',
            category=self.category,
            description='Out of stock item',
            price=40,
            stock_level=0,
            rating=4.9,
            is_available=True,
        )
        self.user = User.objects.create_user(
            username='reco_view_user',
            password='RecoPass123!',
        )

    def test_home_recommendations_logged_in_have_no_duplicates_or_out_of_stock(self):
        self.client.login(username='reco_view_user', password='RecoPass123!')
        response = self.client.get(reverse('store:home'))

        self.assertEqual(response.status_code, 200)
        recommended_products = list(response.context['recommended_products'])
        ids = [product.product_id for product in recommended_products]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn(self.out_of_stock.product_id, ids)

    def test_home_recommendations_anonymous_use_session_history(self):
        session = self.client.session
        session.save()
        session_key = session.session_key

        interaction = UserInteraction.objects.create(
            session_key=session_key,
            product=self.product_1,
            interaction_type='view',
            interaction_count=1,
        )
        UserInteraction.objects.filter(pk=interaction.pk).update(timestamp=timezone.now())

        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        recommended_products = list(response.context['recommended_products'])
        self.assertGreater(len(recommended_products), 0)

    def test_cart_view_exposes_recommendation_sections(self):
        session = self.client.session
        session['cart'] = {
            str(self.product_1.product_id): {
                'name': self.product_1.name,
                'price': float(self.product_1.discount_price),
                'image': '',
                'quantity': 1,
                'product_id': self.product_1.product_id,
            }
        }
        session.save()

        response = self.client.get(reverse('store:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('recommended_products', response.context)
        self.assertIn('trending_products', response.context)
        self.assertIn('recently_viewed_products', response.context)

    def test_recommendations_api_has_unique_active_in_stock_products(self):
        response = self.client.get(reverse('store:api_recommendations'))
        self.assertEqual(response.status_code, 200)
        data = response.json()

        ids = [item['id'] for item in data['recommendations']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn(self.out_of_stock.product_id, ids)


class ProductImportTests(TestCase):
    """Imports from a minimal cleaned CSV in an isolated directory."""

    def test_importer_creates_products_from_cleaned_sample(self):
        csv_body = (
            "product_title,product_category,discounted_price,product_rating,total_reviews\n"
            'Imported Gadget,Electronics,49.99,4.5,10\n'
            'Second Item,Books,12.00,4.0,2\n'
        )
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "amazon_products_sales_data_cleaned.csv").write_text(
                csv_body, encoding="utf-8"
            )
            importer = ProductImporter(base_dir=base)
            summary = importer.import_products(source="cleaned", clear=True, limit=None)

        self.assertGreater(summary.created_products + summary.updated_products, 0)
        self.assertGreaterEqual(summary.total_rows, 1)
        self.assertTrue(
            Product.objects.filter(name__icontains="Imported Gadget").exists()
        )


class ImportProductsCommandTests(TestCase):
    def test_command_runs_when_auto_source_available(self):
        try:
            ProductImporter(base_dir=Path(__file__).resolve().parent.parent).resolve_source(
                "auto"
            )
        except FileNotFoundError:
            self.skipTest(
                "No product CSV in project root — place a valid cleaned/products/uk CSV to test the command."
            )

        out = io.StringIO()
        call_command("import_products", "--limit", "1", stdout=out)
        self.assertIn("Product import completed", out.getvalue())


class PageAndTemplateTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Template Cat", slug="template-cat")
        self.product = Product.objects.create(
            name="Visible Phone",
            slug="visible-phone",
            category=self.category,
            description="For template tests",
            price=199,
            stock_level=5,
            rating=4.2,
            is_available=True,
        )

    def test_home_renders(self):
        response = self.client.get(reverse("store:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_product_list_renders(self):
        response = self.client.get(reverse("store:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/product_list.html")

    def test_product_detail_renders(self):
        url = reverse("store:product_detail", args=[self.product.product_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/product_detail.html")

    def test_search_route_renders_product_list_template(self):
        response = self.client.get(reverse("store:search"), {"q": "Visible"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/product_list.html")

    def test_recommendations_page_renders(self):
        user = User.objects.create_user(username="reco_page_user", password="Pass12345!")
        self.client.login(username="reco_page_user", password="Pass12345!")
        response = self.client.get(reverse("store:recommendations"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/recommendations.html")


class ExternalProductSyncTests(TestCase):
    def setUp(self):
        self.sample_products = [
            {
                'id': 101,
                'title': 'External Phone',
                'description': 'Imported phone',
                'category': 'electronics',
                'price': 499,
                'stock': 30,
                'rating': 4.6,
                'thumbnail': 'https://example.com/phone.jpg',
                'images': ['https://example.com/phone.jpg'],
            },
            {
                'id': 102,
                'title': 'External Backpack',
                'description': 'Imported backpack',
                'category': 'accessories',
                'price': 79,
                'stock': 0,
                'rating': 4.1,
                'thumbnail': 'https://example.com/bag.jpg',
                'images': ['https://example.com/bag.jpg'],
            },
        ]

    def _mock_dummyjson_get(self, *_args, **_kwargs):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {'products': self.sample_products}
        return response

    @patch('store.services.external_products.base.requests.Session.get')
    def test_sync_dummyjson_products(self, mock_get):
        mock_get.side_effect = self._mock_dummyjson_get
        call_command('sync_external_products', '--source', 'dummyjson', '--limit', '2', '--publish', 'false')

        self.assertEqual(ExternalProduct.objects.count(), 2)
        self.assertEqual(Product.objects.count(), 0)

    @patch('store.services.external_products.base.requests.Session.get')
    def test_publish_products(self, mock_get):
        mock_get.side_effect = self._mock_dummyjson_get
        call_command('sync_external_products', '--source', 'dummyjson', '--limit', '2', '--publish', 'true')

        self.assertEqual(ExternalProduct.objects.count(), 2)
        self.assertEqual(Product.objects.count(), 2)
        self.assertGreaterEqual(Category.objects.count(), 2)
        product = Product.objects.get(name='External Phone')
        self.assertTrue(product.manages_local_stock)
        self.assertTrue(product.stock_level > 0)
        self.assertTrue(product.can_add_to_cart)
        self.assertFalse(product.is_affiliate_product)
        self.assertEqual(product.buy_on_source_url, '')

    @patch('store.services.external_products.base.requests.Session.get')
    def test_homepage_detail_and_search_with_imported_products(self, mock_get):
        mock_get.side_effect = self._mock_dummyjson_get
        call_command('sync_external_products', '--source', 'dummyjson', '--limit', '2', '--publish', 'true')

        home_response = self.client.get(reverse('store:home'))
        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, 'External Phone')

        product = Product.objects.get(name='External Phone')
        detail_response = self.client.get(reverse('store:product_detail', args=[product.product_id]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'External Phone')

        search_response = self.client.get(reverse('store:search'), {'q': 'Phone'})
        self.assertEqual(search_response.status_code, 200)
        self.assertContains(search_response, 'External Phone')
        self.assertContains(home_response, 'Add to Cart')
        self.assertNotContains(home_response, 'Buy on Source')

    @patch('store.services.external_products.base.requests.Session.get')
    def test_duplicate_sync_does_not_duplicate_products(self, mock_get):
        mock_get.side_effect = self._mock_dummyjson_get
        call_command('sync_external_products', '--source', 'dummyjson', '--limit', '2', '--publish', 'true')
        call_command('sync_external_products', '--source', 'dummyjson', '--limit', '2', '--publish', 'true')

        self.assertEqual(ExternalProduct.objects.count(), 2)
        self.assertEqual(Product.objects.count(), 2)


class TrainAndGenerateCommandsTests(TestCase):
    """Management commands against isolated recommender artifact directory."""

    def setUp(self):
        self.original_artifact_relative_dir = recommendation_engine.ARTIFACT_RELATIVE_DIR
        self.test_artifact_relative_dir = Path("models") / f"recommender_test_{uuid.uuid4().hex}"
        recommendation_engine.ARTIFACT_RELATIVE_DIR = self.test_artifact_relative_dir
        self.artifact_dir = Path(settings.BASE_DIR) / self.test_artifact_relative_dir
        if self.artifact_dir.exists():
            shutil.rmtree(self.artifact_dir, ignore_errors=True)
        clear_artifact_cache()

        self.category = Category.objects.create(name="Cmd Cat", slug="cmd-cat")
        self.product = Product.objects.create(
            name="Cmd Product",
            slug="cmd-product",
            category=self.category,
            description="Training smoke",
            price=50,
            stock_level=10,
            rating=4.0,
            is_available=True,
        )
        self.user = User.objects.create_user(username="cmd_train_user", password="CmdTrain123!")
        UserInteraction.objects.create(
            user=self.user,
            product=self.product,
            interaction_type="view",
            interaction_count=1,
        )

    def tearDown(self):
        recommendation_engine.ARTIFACT_RELATIVE_DIR = self.original_artifact_relative_dir
        if self.artifact_dir.exists():
            shutil.rmtree(self.artifact_dir, ignore_errors=True)
        clear_artifact_cache()

    def test_train_recommender_management_command(self):
        out = io.StringIO()
        call_command(
            "train_recommender",
            "--top-k",
            "3",
            stdout=out,
            stderr=out,
        )
        text = out.getvalue()
        self.assertIn("Training completed", text)
        self.assertTrue((self.artifact_dir / "config.json").exists())

    def test_generate_recommendations_after_train(self):
        train_recommender_artifacts(top_k=4)
        out = io.StringIO()
        call_command(
            "generate_recommendations",
            "--user-id",
            str(self.user.id),
            "--limit",
            "4",
            stdout=out,
        )
        self.assertIn(self.user.username, out.getvalue())
