from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from diap.models.person import Person


class CallBack(models.Model):
    class Meta:
        verbose_name = 'Повідомлення про помилку'
        verbose_name_plural = 'Повідомлення про помилку'

    class StatusCallBackPostChoices(models.TextChoices):
        DELETED = 'DELETED', _('Deleted')
        PUBLISHED = 'PUBLISHED', _('Published')
        PROCESSING = 'PROCESSING', _('Processing')


    title = models.CharField(max_length=501, verbose_name='Назва для зворотнього зв\'язку')
    text = models.TextField(max_length=250, verbose_name='Текст для зворотнього зв\'язку')
    published = models.CharField(
        max_length=20, choices=StatusCallBackPostChoices.choices,
        default=StatusCallBackPostChoices.PROCESSING,
        verbose_name='Статус обробки'
    )
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Час створення')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Час зміни')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='callback_user')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name='person', related_name="callback_person")

    def __str__(self):
        return self.title
