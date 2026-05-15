import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product, UserInteraction


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
