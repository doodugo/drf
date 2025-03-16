from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from inventory.models import PhotoCard
from transactions.models import Sale
class BuyTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='test_buyer@test.com',
            username='testuser',
            password='testpassword',
            user_type='buyer',
        )


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



