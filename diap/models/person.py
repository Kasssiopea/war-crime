from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
# Create your models here.
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from diap.models.choices import (
    PersonTypeSocialNetworkChoices,
    StatusPersonChoices,
    StatusPersonPostChoices,
    StatusPersonPostPublished, ArmyRangChoices, ArmyTypeChoices, DateMonth, DateDay,
)


class Person(models.Model):
    # -- Main information about Person -- #
    for_adding = models.TextField(max_length=9999, blank=True, null=True, verbose_name='Текст для модерації')
    img_for_adding = models.CharField(max_length=500, blank=True, null=True, verbose_name='Зоображення для додавання')

    first_name = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Ім\'я'))
    last_name = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Прізвище'))
    middle_name = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('По батькові'))

    birthday = models.DateField(blank=True, null=True, verbose_name=_('Дата народження'))
    birthday_year = models.IntegerField(
        validators=[MinValueValidator(1950), MaxValueValidator(2025)],
        blank=True, null=True,
        verbose_name=_('Рік народження'))

    birthday_month = models.CharField(max_length=64, blank=True, null=True,
                                      choices=DateMonth.choices,
                                      verbose_name=_('Місяць народження'))

    birthday_day = models.CharField(max_length=64, blank=True, null=True,
                                    choices=DateDay.choices,
                                    verbose_name=_('День народження'))

    # vik = models.SmallIntegerField(blank=True, null=True, verbose_name='Вік')
    citizenship = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Громадянство'))
    passport = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Паспорт'))
    individual_identification_number = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name=_('Індитифікаційний код'
    ))
    place_of_birthday = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Місце народження'))
    place_of_living = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('Місце проживання'))
    additional_info = models.TextField(max_length=9999, blank=True, null=True, verbose_name=_('Додаткова інформація'))
    source = models.TextField(max_length=2000, blank=True, null=True, verbose_name=_('Джерело'))
    # -- Military Person fields -- #
    rank = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Військове звання'))

    rank_choice = models.CharField(max_length=64,
                                   blank=True,
                                   null=True,
                                   choices=ArmyRangChoices.choices,
                                   verbose_name=_('Військове звання'))

    job_title = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('Посада'))
    military_unit = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Військова частина'))
    type_of_army = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('Рід військ'))

    type_of_army_choice = models.CharField(max_length=64,
                                           blank=True,
                                           null=True,
                                           choices=ArmyTypeChoices.choices,
                                           verbose_name=_('Рід військ'))

    military_from = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name=_('Місце знаходження військової частини'
    ))
    commander = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Командир'))

    # -- Person status & what's happends
    status_person = models.CharField(
        max_length=32,
        choices=StatusPersonChoices.choices,
        default=StatusPersonChoices.DIE,
        verbose_name=_('Статус'
    ))

    place_where_accident = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('Місце смерті'))

    data_when_accident = models.DateField(default=None, blank=True, null=True, verbose_name=_('Дата смерті'))
    data_when_accident_year = models.IntegerField(
        validators=[MinValueValidator(1940), MaxValueValidator(2025)],
        blank=True, null=True,
        verbose_name=_('Рік смерті'))

    data_when_accident_month = models.CharField(max_length=64, blank=True, null=True,
                                                choices=DateMonth.choices,
                                                verbose_name=_('Місяць смерті'))

    data_when_accident_day = models.CharField(max_length=64, blank=True, null=True,
                                              choices=DateDay.choices,
                                              verbose_name=_('День смерті'))

    place_of_rip = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Місце поховання'))

    place_of_rip_date_year = models.IntegerField(
        validators=[MinValueValidator(1950), MaxValueValidator(2025)],
        blank=True, null=True,
        verbose_name=_('Рік поховання'))

    place_of_rip_date_month = models.CharField(max_length=64, blank=True, null=True,
                                               choices=DateMonth.choices,
                                               verbose_name=_('Місяць поховання'))

    place_of_rip_date_day = models.CharField(max_length=64, blank=True, null=True,
                                             choices=DateDay.choices,
                                             verbose_name=_('Дата поховання'))

    # -- Date log -- #
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_('Час створення'))
    time_update = models.DateTimeField(auto_now=True, verbose_name=_('Час останьої зміни'))
    # -- Post status -- #
    post_status = models.CharField(
        max_length=32,
        choices=StatusPersonPostChoices.choices,
        default=StatusPersonPostChoices.FOR_MODERATION,
        verbose_name=_('Статус поста')
    )

    publish_status = models.CharField(
        max_length=32,
        choices=StatusPersonPostPublished.choices,
        default=StatusPersonPostPublished.NOTPUBLISHED,
        verbose_name=_('Статус публікації')
    )

    take_task = models.CharField(null=True, max_length=250, default='not taken')

    task_published = models.CharField(blank=True, null=True, max_length=256, verbose_name='Опублікував')
    task_published_date = models.DateTimeField(blank=True, null=True, auto_now=False)

    task_deleted = models.CharField(blank=True, null=True, max_length=256, verbose_name='Видалив')
    task_deleted_date = models.DateTimeField(blank=True, null=True, auto_now=False)

    task_processing = models.CharField(blank=True, null=True, max_length=256, verbose_name='Доопрацювання')
    task_processing_date = models.DateTimeField(blank=True, null=True, auto_now=False)

    task_for_check = models.CharField(blank=True, null=True, max_length=256, verbose_name='Опрацював')
    task_for_check_date = models.DateTimeField(blank=True, null=True, auto_now=False)
     
    # -- Absolute url Method -- #
    def get_absolute_url(self):
        path = reverse('person', kwargs={'post_person_pk': self.pk}).replace('/ru', '').replace('/uk', '').replace('/en', '')
        return f'https://poternet.site{path}'

    def return_table(self):
        fild_name = self.last_name
        return fild_name

    # -- Split source Method -- #
    # -- Absolute url Method -- #
    def source_as_list(self):
        if self.source:
            return self.source.split("\n")


class PersonImage(models.Model):
    image = models.ImageField(upload_to="photos/%Y/%m/%d", blank=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, related_name='images')
    main_image = models.BooleanField(default=False, verbose_name='Головне фото')
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def image_return(self):
        fild_name = 'Image: ' + self.person.last_name + ' ' + self.person.first_name + ' ' + self.person.middle_name
        return fild_name


class SoursePersonImage(models.Model):
    image = models.ImageField(upload_to="photos/%Y/%m/%d")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, related_name='source_images')
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def image_return(self):
        fild_name = 'Image: ' + self.person.last_name + ' ' + self.person.first_name + ' ' + self.person.middle_name
        return fild_name


class PersonText(models.Model):
    text_url = models.CharField(max_length=1024, blank=True, null=True, verbose_name='Посилання на текст')
    text_from = models.CharField(max_length=128, verbose_name='Звідки текст (Домен)')
    text = models.TextField(verbose_name='Текст')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Час створення')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Час останьої зміни')

    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, related_name='texts')

    def __str__(self):
        fild_name = 'Text: ' + self.person.last_name + ' ' + self.person.first_name + ' ' + self.person.middle_name
        return fild_name


class PersonPlaceWhereHeWas(models.Model):
    place = models.CharField(max_length=128, verbose_name='Місця дислокації')

    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Час створення')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Час останьої зміни')

    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, related_name='place_where_he_was')

    def __str__(self):
        fild_name = 'Text: ' + self.person.last_name + ' ' + self.person.first_name + ' ' + self.person.middle_name
        return fild_name


class PersonSocialNetwork(models.Model):
    type = models.ForeignKey(PersonTypeSocialNetworkChoices, on_delete=models.CASCADE, verbose_name='Тип')
    profile = models.CharField(max_length=128, verbose_name='Посилання на профіль')
    profile_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='Логін профілю')

    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Час створення')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Час останьої зміни')

    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, related_name='social_networks')


