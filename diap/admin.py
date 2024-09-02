from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import ngettext

from .models.callback import CallBack
from .models.choices import PersonTypeSocialNetworkChoices, StatusPersonPostPublished, StatusPersonPostChoices
from .models.front import NewsDead, ImportantNews
from .models.partners import Partners
from .models.person import Person, PersonImage, SoursePersonImage, PersonText, PersonPlaceWhereHeWas, \
    PersonSocialNetwork
from django.db.models import Q, Count

from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter, AdminSite

from .models.telegram import TelegramUser


class PersonSocialNetworkAdmin(admin.ModelAdmin):
    title = 'SocialNetwork'


class PersonSocialNetworkInline(admin.StackedInline):
    model = PersonSocialNetwork
    max_num = 10
    extra = 0


class PersonPlaceWhereHeWasAdmin(admin.ModelAdmin):
    pass


class PersonPlaceWhereHeWasInline(admin.StackedInline):
    model = PersonPlaceWhereHeWas
    max_num = 10
    extra = 0


class PersonTextAdmin(admin.ModelAdmin):
    pass


class PersonTextInline(admin.StackedInline):
    model = PersonText
    max_num = 10
    extra = 0


class PersonImageAdmin(admin.ModelAdmin):
    pass


class PersonImageInline(admin.StackedInline):
    model = PersonImage
    max_num = 10
    extra = 0


class SoursePersonImageAdmin(admin.ModelAdmin):
    pass


class SoursePersonImageInline(admin.StackedInline):
    model = SoursePersonImage
    max_num = 10
    extra = 0


class ImageFilter(SimpleListFilter):
    title = 'images'  # or use _('country') for translated title
    parameter_name = 'images'

    def lookups(self, request, model_admin):
        return (
            ('With', _('With image')),
            ('Without', _('Without image')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'With':
            return queryset.filter(images__image__isnull=False).annotate(num_images=Count('images'))
        if self.value() == 'Without':
            return queryset.filter(images__image__isnull=True).annotate(num_images=Count('images'))

class GroupFilter(admin.SimpleListFilter):
    title = 'Group'
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        groups = Group.objects.all()
        return [(group.id, group.name) for group in groups]

    def queryset(self, request, queryset):
        if self.value():
            users_name = User.objects.all().filter(groups__id=self.value()).values('username')
            print(users_name)
            return queryset.filter(take_task__in=users_name)
        return queryset

class PersonAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'middle_name', 'pk', 'data_when_accident')
    list_display = ['pk', 'last_name', 'first_name', 'middle_name', 'time_update', 'post_status',
                    'get_user_group']
    list_filter = (
        'time_update',
        'post_status',
        ('take_task', DropdownFilter),
        ('task_for_check', DropdownFilter),
        ('place_of_rip_date_year', DropdownFilter),
        ('data_when_accident_year', DropdownFilter),
        'publish_status',
        ImageFilter,
        GroupFilter
    )
    ordering = ['time_update']
    inlines = [PersonImageInline, SoursePersonImageInline, PersonSocialNetworkInline, PersonTextInline,
               PersonPlaceWhereHeWasInline]
    actions = ['make_published_person', 'make_unpublished_person', 'make_deleted_person',
               'Add_the_selected_files_in_the_entry_personal', 'delete_the_selected_files_to_a_personal_record',
               'change_puplished', 'return_record']

    readonly_fields = ['publish_status', ]

    fields = (
        'for_adding',
        'img_for_adding',
        'last_name',
        'first_name',
        'middle_name',
        'birthday',
        ('birthday_day', 'birthday_month', 'birthday_year'),
        'citizenship',
        'passport',
        'individual_identification_number',
        'place_of_birthday',
        'place_of_living',
        'additional_info',
        'source',
        'type_of_army_choice',
        'rank_choice',
        'job_title',
        'military_unit',
        'military_from',
        'status_person',
        'place_where_accident',
        'data_when_accident',
        ('data_when_accident_day', 'data_when_accident_month', 'data_when_accident_year'),
        'place_of_rip',
        ('place_of_rip_date_day', 'place_of_rip_date_month', 'place_of_rip_date_year'),
        'post_status',
        'publish_status',
        'task_published',
        'task_deleted',
        'task_for_check'
    )

    def save_model(self, request, obj, form, change):
        if obj.publish_status == StatusPersonPostPublished.PUBLISHED:
            obj.post_status = StatusPersonPostPublished.PUBLISHED

        if obj.post_status == StatusPersonPostChoices.FORCHECK:
            obj.task_for_check = request.user.get_username()
            obj.task_for_check_date = timezone.now()

        if obj.post_status == StatusPersonPostPublished.PUBLISHED and not obj.task_published:
            # Если поле post_status становится published в первый раз и поле task_published не заполнено
            obj.task_published = request.user.get_username()
            obj.task_published_date = timezone.now()

        if obj.post_status == StatusPersonPostChoices.PROCESSING:
            obj.task_processing = request.user.get_username()
            obj.task_processing_date = timezone.now()

        if obj.post_status == StatusPersonPostChoices.DELETED and not obj.task_deleted:
            obj.task_deleted = request.user.get_username()
            obj.task_deleted_date = timezone.now()
            
        obj.take_task = request.user.get_username()
        super(PersonAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request, *args, **kwargs):
        user_groups = request.user.groups.all()
        groups = ['CHNUVS', 'NAVS', 'DIAP', 'DDUVS', 'LDUVS', 'ODUVS']
        group = user_groups.filter(name__in=groups)
        if group:
            users = User.objects.all().filter(groups__in=group)
            u = [i.username for i in users]
        else:
            u = []
        if request.user.is_superuser:
            return super(PersonAdmin, self).get_queryset(request, *args, **kwargs)
        elif user_groups.filter(name='moderator_mid').exists():
            if user_groups.filter(name='Incoming').exists():
                return super(PersonAdmin, self).get_queryset(request, *args, **kwargs).filter(
                    Q(post_status__in=['FORCHECK', 'DELETED', 'PROCESSING', 'PUBLISHED', 'FOR_MODERATION', 'INCOMING'])).filter(
                    Q(take_task='not taken') | Q(take_task__in=u) | Q(post_status='PUBLISHED'))
            return super(PersonAdmin, self).get_queryset(request, *args, **kwargs).filter(
                Q(post_status__in=['FORCHECK', 'DELETED', 'PROCESSING', 'PUBLISHED', 'FOR_MODERATION'])).filter(
                Q(take_task='not taken') | Q(take_task__in=u) | Q(post_status='PUBLISHED'))
        else:
            return super(PersonAdmin, self).get_queryset(request, *args, **kwargs).filter(
                Q(post_status__in=['FOR_MODERATION', 'PROCESSING', 'DELETED'])).filter(
                Q(take_task='not taken') | Q(take_task=f'{request.user.get_username()}'))

    @admin.action(description='Mark selected person as published')
    def make_published_person(self, request, queryset):
        updated = queryset.update(post_status='PUBLISHED')
        self.message_user(request, ngettext(
            '%d Person was successfully marked as published.',
            '%d Persons were successfully marked as published.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Mark selected person as unpublished')
    def make_processing_person(self, request, queryset):
        updated = queryset.update(post_status='PROCESSING')
        self.message_user(request, ngettext(
            '%d Person was successfully marked as processing.',
            '%d Persons were successfully marked as processing.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Mark selected person as deleted')
    def make_deleted_person(self, request, queryset):
        updated = queryset.update(post_status='DELETED')
        self.message_user(request, ngettext(
            '%d Person was successfully marked as deleted.',
            '%d Persons were successfully marked as deleted.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Add selected records for moderation')
    def Add_the_selected_files_in_the_entry_personal(self, request, queryset):
        updated = queryset.update(take_task=f'{request.user.get_username()}')
        self.message_user(request, ngettext(
            '%d The person has been successfully marked for moderation',
            '%d The person has been successfully marked for moderation',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='Delete selected records')
    def delete_the_selected_files_to_a_personal_record(self, request, queryset):
        updated = queryset.update(take_task='not taken')
        self.message_user(request, ngettext(
            '%d The recording was successfully removed from personal entries',
            '%d The recording was successfully removed from personal entries',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='change_puplished')
    def change_puplished(self, request, queryset):
        updated = queryset.update(post_status='FOR_MODERATION', publish_status='NOTPUBLISHED')
        self.message_user(request, ngettext(
            '%d The recording was successfully removed from personal entries',
            '%d The recording was successfully removed from personal entries',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description='send post back to moderator')
    def return_record(self, request, queryset):
        for person in queryset:
            task_for_check = person.task_for_check
            person.post_status = StatusPersonPostChoices.FOR_MODERATION
            person.take_task = task_for_check
            person.save()
        self.message_user(request, ngettext(
            '%d The recording was successfully return',
            '%d The recording was successfully return',
            queryset.count()
        ) % queryset.count(), messages.SUCCESS)
    # 1 - moderator_junior
    # 2 - administrator
    # 3 - moderator_mid
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Если запись уже сохранена в базе данных
            read_only = [
                'task_published',
                'task_deleted',
                'task_for_check',
                'status_person'
            ]
            if request.user.is_superuser:
                return read_only
            if obj.task_published:
                user_group = check_group(request.user.get_username())
                creator_group = check_group(obj.task_published)
                if any(item in user_group for item in creator_group):
                    return read_only  # Поле будет только для чтения
                else:
                    read_only.append('post_status')
                    return read_only
            return read_only

        allowed_groups = [2, 3]
        if request.user.groups.filter(id__in=allowed_groups).exists():
            # группа модераторов разрешена для изменения поля
            return []
        else:
            # группа модераторов не имеет доступа к изменению поля
            return self.readonly_fields + ['take_task']  # Добавляем поле в список только для чтения

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.fields + ('take_task',)
        return self.fields

    @admin.display()
    def person_with_image(self, obj):
        if obj.images.all():
            return 'Have image'
        return 'None'

    @admin.display()
    def get_user_group(self, obj):
        if obj.take_task:
            groups = ['CHNUVS', 'NAVS', 'DIAP', 'DDUVS', 'LDUVS', 'ODUVS']
            user = User.objects.all().filter(username=obj.take_task).first()
            if user:
                if user.groups.filter(name__in=groups).exists():
                    return list(user.groups.values_list('name', flat=True))
                elif user.is_superuser:
                    return 'Admin'
                else:
                    return 'User not contain in groups'
            else:
                return 'User undefined'
        return 'None'



class PersonTypeSocialNetworkAdmin(admin.ModelAdmin):
    list_display = ['type', 'time_create']
    ordering = ['type']


# NEWS FRONT
class NewsDeadAdmin(admin.ModelAdmin):
    search_fields = ('time_create', 'published')
    list_display = ['image', 'published', 'time_create', 'user']
    exclude = ('user',)

    def get_queryset(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super(NewsDeadAdmin, self).get_queryset(request)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        if formset.model == NewsDead:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
                instance.save()
        else:
            formset.save()


class CallBackAdmin(admin.ModelAdmin):
    search_fields = ('user', 'person', 'time_create')
    list_display = ['title', 'user', 'person', 'time_create', 'published']
    list_filter = ['published', ]

    def get_queryset(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super(CallBackAdmin, self).get_queryset(request)


class PartnersAdmin(admin.ModelAdmin):
    search_fields = ('name', 'url', 'published', 'time_create')
    list_display = ['name', 'url', 'published', 'time_create']
    list_filter = ['published', ]

    def get_queryset(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super(PartnersAdmin, self).get_queryset(request)


# -- Admin add models -- #
admin.site.register(Person, PersonAdmin)
admin.site.register(PersonTypeSocialNetworkChoices, PersonTypeSocialNetworkAdmin)

# NEWS
admin.site.register(NewsDead, NewsDeadAdmin)

# Partners

admin.site.register(model_or_iterable=Partners, admin_class=PartnersAdmin)

# CALLBACK
admin.site.register(CallBack, CallBackAdmin)

# IMPORTANT NEWS
admin.site.register(ImportantNews)


# Telegram Users
class TelegramUserAdmin(admin.ModelAdmin):
    search_fields = ('telegram_id', 'username', 'language')
    list_display = ['telegram_id', 'username', 'language']
    list_filter = ['language', ]

    def get_queryset(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super(TelegramUserAdmin, self).get_queryset(request)


admin.site.register(TelegramUser, TelegramUserAdmin)

def check_group(username: str) -> list:
    allowed_groups = ['CHNUVS', 'NAVS', 'DIAP', 'DDUVS', 'LDUVS', 'ODUVS']
    user = User.objects.all().filter(username=username).first()
    group_names = [group.name for group in user.groups.all()]
    return [group for group in group_names if group in allowed_groups]
