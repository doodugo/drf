from django.db import models
from conf.models import TimeStampedModel
from django.db import transaction

class CashLog(TimeStampedModel):
    user_id = models.ForeignKey(
        to='accounts.User',
        on_delete=models.DO_NOTHING,
        related_name='cash_logs',
        help_text = '사용자 ID'
    )

    cash = models.IntegerField(
        null=False,
        help_text = '적립/사용 캐시 (+는 적립, -는 사용으로 가정)'
    )

    created_date = models.DateTimeField(
        help_text = '이력 발생 일시',
        auto_now_add=True,
    )

    def __str__(self):
        return f"User {self.user_id.username}: {self.cash}원 ({self.created_date})"

    WELCOME_CASH = 30000
    @classmethod
    def create_welcome_cash(cls, user_id):
        cls.objects.create(
            user_id=user_id,
            cash=cls.WELCOME_CASH,
        )

    #DEPRECATED
    @classmethod
    def total_cash(cls, user_id):
        total_cash = cls.objects.filter(user_id=user_id).aggregate(
            total_cash=models.Sum('cash'))['total_cash'] or 0
        return total_cash

    @transaction.atomic
    def save(self, *args, **kwargs):
        user = self.user_id
        user.total_cash += self.cash
        user.save()
        super().save(*args, **kwargs)


class Sale(TimeStampedModel):
    user_id = models.ForeignKey(
        to='accounts.User',
        on_delete=models.DO_NOTHING,
        related_name='sales',
        help_text = '사용자 ID',
        null=False,
        blank=False,
    )

    photo_card_id = models.ForeignKey(
        to='inventory.PhotoCard',
        on_delete=models.DO_NOTHING,
        related_name='sales',
        help_text = '포토카드 ID',
        null=False,
        blank=False,
    )

    amount = models.IntegerField(
        help_text = '등록 수량',
        null=False,
        blank=False,
    )

    price = models.PositiveIntegerField(
        help_text = '장 당 가격',
        null=False,
        blank=False,
    )

    def __str__(self):
        return f" \
            {self.user_id.username}: {self.photo_card_id.name} \
            - {self.amount}장 ({self.price}원)"

    @classmethod
    def purchase_commission(cls, price):
        if price < 15000:
            return 0.062
        return 0.137

    @property
    def buy_price(self):
        return self.price + int(self.price * self.purchase_commission(self.price))

    def save(self, *args, **kwargs):
        if not self.user_id.is_seller:
            raise ValueError("판매자만 판매 가능합니다.")
        super().save(*args, **kwargs)


class Buy(TimeStampedModel):
    user_id = models.ForeignKey(
        to='accounts.User',
        on_delete=models.DO_NOTHING,
        related_name='buys',
        help_text = '사용자 ID',
    )

    sale_id = models.ForeignKey(
        to='transactions.Sale',
        on_delete=models.DO_NOTHING,
        related_name='buys',
        help_text = '판매 ID',
    )

    amount = models.IntegerField(
        help_text = '구매 수량',
        null=False,
        blank=False,
    )    

    @property
    def total_delivery_price(self):
        if self.amount >= 10:
            return 500 + DeliveryRequest.SHIPMENT_PRICE
        else:
            return 1000 + DeliveryRequest.SHIPMENT_PRICE


class DeliveryRequest(TimeStampedModel):
    '''
        구매자가 배송 요청을 해야하기에 구매 로직과 결합 하지 않을 예정
        이미 배송이 요청되었는지 상태 체크를 위해 is_requested 사용
        중복 배송을 막기 위해 buy_id와 결합 할 예정
        추후 amount와 관련이 있을 수 있지만 현재 단계 고려하지 않음x
    '''

    STATUS_CHOICES = [
        ('PENDING', '대기'),
        ('REQUESTED', '요청'),
        ('DELIVERED', '배송완료'),
        ('CANCELLED', '취소'),
    ]

    SHIPMENT_PRICE = 1500

    user_id = models.ForeignKey(
        to='accounts.User',
        on_delete=models.DO_NOTHING,
        related_name='delivery_requests',
        help_text = '사용자 ID',
    )

    buy_id = models.ForeignKey(
        to='transactions.Buy',
        on_delete=models.DO_NOTHING,
        related_name='delivery_requests',
        help_text = '구매 ID',
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='REQUESTED',
        help_text = '배송 상태',
    )

    address = models.CharField(
        max_length=255,
        help_text = '배송 주소',
    )

    postal_code = models.CharField(
        max_length=5,
        help_text = '우편번호',
    )

    @property
    def is_requested(self):
        return self.status == 'REQUESTED'

