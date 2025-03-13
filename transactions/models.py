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
