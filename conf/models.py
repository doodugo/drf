from django.db import models

class TimeStampedModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    deleted_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
