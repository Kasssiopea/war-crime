# Generated by Django 4.1.7 on 2023-05-10 06:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diap', '0027_alter_telegramuser_telegram_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='data_when_accident_year',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1940), django.core.validators.MaxValueValidator(2025)], verbose_name='Рік смерті'),
        ),
    ]
