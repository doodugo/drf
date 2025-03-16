from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from inventory.models import PhotoCard
from transactions.models import Buy, CashLog, Sale
from django.urls import reverse
from rest_framework import status


class BuyTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        signup_url = reverse('signup')
        self.user_data = {
            'email': 'test_buyer@test.com',
            'username': 'testuser',
            'password': 'testpassword',
            'user_type': 'buyer',
        }
        self.client.post(signup_url, self.user_data, format='json')
        self.user = User.objects.get(email=self.user_data['email'])
        self.client.force_authenticate(user=self.user)

        seller = User.objects.create_user(
            email='test_seller@test.com',
            username='test_seller',
            password='test_seller_password',
            user_type='seller',
        )

        photo_card = PhotoCard.objects.create(
            name='test_photo_card',
            artist_name='test_artist_name',
            group_name='test_group_name',
        )
        self.sale = Sale.objects.create(
            user_id=seller,
            photo_card_id=photo_card,
            amount=10,
            price=20000,
        )
        self.data = {
            'sale_id': self.sale.id,
            'amount': 1,
        }

    def test_buy_successful(self):
        url = reverse('buys-list')
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Buy.objects.filter(user_id=self.user).count(), 1)

        self.sale.refresh_from_db()
        self.assertEqual(self.sale.amount, 9)

        total_reduce_cash = self.sale.buy_price * self.data['amount']
        self.assertEqual(CashLog.total_cash(self.user), CashLog.WELCOME_CASH - total_reduce_cash)
        self.assertEqual(CashLog.objects.filter(user_id=self.user).count(), 2)
        self.assertEqual(CashLog.objects.last().cash, -total_reduce_cash)

