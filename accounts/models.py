import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('seller', '판매자'),
        ('buyer', '구매자'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, blank=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=False)
    username = models.CharField(max_length=20, blank=False, help_text='이름')
    total_cash = models.IntegerField(default=0, help_text='총 캐시')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type', 'password']

    def __str__(self):
        return f'{self.username} ({self.user_type})'

    @property
    def is_seller(self):
        return self.user_type == 'seller'

    @property
    def is_buyer(self):
        return self.user_type == 'buyer'
