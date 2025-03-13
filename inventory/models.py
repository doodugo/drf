from conf.models import TimeStampedModel
from django.db import models


class PhotoCard(TimeStampedModel):
    name = models.CharField(
        max_length=100,
        null=False,
        help_text='포토카드 명'
    )

    artist_name = models.CharField(
        max_length=30,
        null=False,
        help_text='아티스트 명'
    )

    group_name = models.CharField(
        max_length=30,
        null=False,
        default='',
        help_text='아티스트 그룹명'
    )

    def __str__(self):
        return f"{self.name} - {self.artist_name}"
