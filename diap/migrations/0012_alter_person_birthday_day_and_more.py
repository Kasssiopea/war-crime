# Generated by Django 4.1.7 on 2023-04-17 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diap', '0011_person_data_when_accident_day_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='birthday_day',
            field=models.CharField(blank=True, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), ('31', '31')], max_length=64, null=True, verbose_name='День народження'),
        ),
        migrations.AlterField(
            model_name='person',
            name='data_when_accident',
            field=models.DateField(blank=True, default=None, null=True, verbose_name='Дата смерті'),
        ),
        migrations.AlterField(
            model_name='person',
            name='data_when_accident_day',
            field=models.CharField(blank=True, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), ('31', '31')], max_length=64, null=True, verbose_name='День смерті'),
        ),
        migrations.AlterField(
            model_name='person',
            name='data_when_accident_month',
            field=models.CharField(blank=True, choices=[('1', 'Січень | Январь'), ('2', 'Лютий | Февраль'), ('3', 'Березень | Март'), ('4', 'Квітень | Апрель'), ('5', 'Травень | Май'), ('6', 'Червень | Июнь'), ('7', 'Липень | Июль'), ('8', 'Серпень | Август'), ('9', 'Вересень | Сентябрь'), ('10', 'Жовтень | Октябрь'), ('11', 'Листопад | Ноябрь'), ('12', 'Грудень | Декабрь')], max_length=64, null=True, verbose_name='Місяць смерті'),
        ),
        migrations.AlterField(
            model_name='person',
            name='place_of_rip_date_day',
            field=models.CharField(blank=True, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), ('31', '31')], max_length=64, null=True, verbose_name='Дата поховання'),
        ),
        migrations.AlterField(
            model_name='person',
            name='place_where_accident',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Місце смерті'),
        ),
    ]
