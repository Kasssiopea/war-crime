from django.db import models


class Partners(models.Model):
    class Meta:
        verbose_name = 'Партнери'
        verbose_name_plural = 'Партнери'

    name = models.CharField(max_length=128, verbose_name='Ім\'я')
    url = models.URLField(verbose_name='Посилання')
    image = models.ImageField(upload_to="partner/%Y/%m/%d")
    published = models.BooleanField(default=False, verbose_name='Статус публікації')

    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

