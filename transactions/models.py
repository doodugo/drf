from django.db import models
from conf.models import TimeStampedModel


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
