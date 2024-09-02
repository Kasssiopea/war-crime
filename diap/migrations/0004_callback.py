# Generated by Django 4.1.7 on 2023-03-22 13:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('diap', '0003_newsdead'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallBack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=501, verbose_name="Назва для зворотнього зв'язку")),
                ('text', models.TextField(max_length=250, verbose_name="Текст для зворотнього зв'язку")),
                ('published', models.CharField(choices=[('DELETED', 'Deleted'), ('PUBLISHED', 'Published'), ('PROCESSING', 'Processing')], default='PROCESSING', max_length=20, verbose_name='Статус обробки')),
                ('time_create', models.DateTimeField(auto_now_add=True, verbose_name='Час створення')),
                ('time_update', models.DateTimeField(auto_now=True, verbose_name='Час зміни')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='callback_person', to='diap.person', verbose_name='person')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='callback_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Зворотній зв'язок",
                'verbose_name_plural': "Зворотній зв'язок",
            },
        ),
    ]
