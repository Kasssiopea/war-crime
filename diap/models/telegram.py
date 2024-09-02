from django.db import models
from django.utils.translation import gettext_lazy as _


class TelegramUser(models.Model):
    class Meta:
        verbose_name = _('Користувач Telegram')
        verbose_name_plural = _('Користувачі Telegram')

    class TelegramUserLangChoices(models.TextChoices):
        LANGUAGE_RU = 'RU', _('Русский язык')
        LANGUAGE_EN = 'EN', _('English language')
        LANGUAGE_UK = 'UK', _('Українська мова')

    telegram_id = models.IntegerField(verbose_name='Telegram user id', unique=True)
    first_name = models.CharField(max_length=128, null=True, blank=True, verbose_name="Ім'я")
    last_name = models.CharField(max_length=128, null=True, blank=True, verbose_name="Прізвище")
    username = models.CharField(max_length=128, null=True, blank=True, verbose_name="Username")
    language = models.CharField(
        max_length=2,
        choices=TelegramUserLangChoices.choices,
        default=TelegramUserLangChoices.LANGUAGE_UK,
        verbose_name=_('Мова користувача')
    )
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Час створення')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Час останьої зміни')

    def __str__(self):
        return self.telegram_id


