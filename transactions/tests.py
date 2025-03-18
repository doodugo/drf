import time
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from inventory.models import PhotoCard
from transactions.models import Buy, CashLog, Sale
from django.urls import reverse
from rest_framework import status
from django.utils import timezone

class BuyTestCase(TestCase):
    def setUp(self):
        '''
            구매 테스트 케이스 설정
            signup url을 통해 welcome cash를 받은 구매자 계정 생성
            time.sleep(1)을 통해 race condition 방지
        '''
        time.sleep(1)
        self.url = reverse('buys-list')
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

        self.seller = User.objects.create_user(
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
            user_id=self.seller,
            photo_card_id=photo_card,
            amount=10,
            price=20000,
        )
        self.data = {
            'sale_id': self.sale.id,
            'amount': 1,
        }

    def test_buy_successful(self):
        '''
            구매 성공 로직
        '''
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Buy.objects.filter(user_id=self.user).count(), 1)

        self.sale.refresh_from_db()
        self.assertEqual(self.sale.amount, 9)

        total_reduce_cash = self.sale.buy_price * self.data['amount']
        self.assertEqual(self.user.total_cash, CashLog.WELCOME_CASH - total_reduce_cash)
        self.assertEqual(CashLog.objects.filter(user_id=self.user).count(), 2)
        self.assertEqual(CashLog.objects.last().cash, -total_reduce_cash)

    def test_buy_failed_zero_amount(self):
        '''
            구매 수량이 0인 경우 구매 실패
        '''
        self.data['amount'] = 0
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_failed_over_amount(self):
        '''
            구매 수량이 판매 수량을 초과하는 경우 구매 실패
        '''
        self.data['amount'] = 11
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_buy_failed_sale_not_exist(self):
        '''
            판매 상품이 존재하지 않는 경우 구매 실패
        '''
        self.data['sale_id'] = 0
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_failed_sale_deleted(self):
        '''
            판매 상품이 삭제된 경우 구매 실패
        '''
        self.sale.deleted_date = timezone.now()
        self.sale.save()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_failed_not_buyer(self):
        '''
            구매자가 아닌 경우 구매 실패
        '''
        self.client.logout()
        self.client.force_authenticate(user=self.seller)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_failed_not_enough_cash(self):
        '''
            캐시가 부족한 경우 구매 실패
        '''
        self.data['amount'] = 3
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("캐시가 부족합니다", response.data['non_field_errors'])
