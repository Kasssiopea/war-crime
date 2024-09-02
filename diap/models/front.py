from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

class NewsDead(models.Model):
    class Meta:
        verbose_name = _('Новини з втратами РФ')
        verbose_name_plural = _('Новини з втратами РФ')

    image = models.ImageField(upload_to="News/%Y/%m/%d", verbose_name='Картинка')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='images_news_dead')
    published = models.BooleanField(default=False, verbose_name='Статус публікації')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Час створення')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Час зміни')

    def __str__(self):
        return f'Новина з втратами {str(self.time_create)}'


class ImportantNews(models.Model):
    class Meta:
        verbose_name = 'Важливі новини'
        verbose_name_plural = 'Важливі новини'

    title = models.CharField(max_length=256, verbose_name='Назва')
    text = models.CharField(max_length=256, verbose_name='Текст')
    span_date = models.CharField(max_length=256,
                                 verbose_name='Дата публікації',
                                 help_text='Приклад вводу 17/04/2023 13:15')
    url_news = models.URLField(max_length=200, verbose_name='Url публікації', help_text='Посилання на новину')
    news_name = models.CharField(max_length=256, verbose_name='Звідки новина')
    image = models.ImageField(upload_to="ImportantDead/%Y/%m/%d", verbose_name='Картинка')

    published = models.BooleanField(default=False, verbose_name='Статус публікації')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Час створення')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Час зміни')

    def __str__(self):
        return self.title

