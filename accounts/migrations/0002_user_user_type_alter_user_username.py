# Generated by Django 4.2 on 2025-03-15 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('seller', '판매자'), ('buyer', '구매자')], default='buyer', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='이름', max_length=20),
        ),
    ]
