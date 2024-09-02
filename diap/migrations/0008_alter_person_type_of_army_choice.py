# Generated by Django 4.1.7 on 2023-03-27 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diap', '0007_alter_person_type_of_army_choice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='type_of_army_choice',
            field=models.CharField(blank=True, choices=[('Сухопутные войска', 'Сухопутные войска'), ('Воздушно-космические силы', 'Воздушно-космические силы'), ('Военно-Морской Флот', 'Военно-Морской Флот'), ('Ракетные войска стратегического назначения', 'Ракетные войска стратегического назначения'), ('Воздушно-десантные войска', 'Воздушно-десантные войска'), ('Войска национальной гвардии Российской Федерации', 'Войска национальной гвардии Российской Федерации'), ('ЧВК', 'ЧВК'), ('МВД', 'МВД'), ('Другие подразделения МО РФ', 'Другие подразделения МО РФ')], max_length=64, null=True, verbose_name='Рід військ - '),
        ),
    ]
