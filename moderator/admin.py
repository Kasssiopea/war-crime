# from django.contrib import admin, messages
from django.utils.translation import ngettext
from django.contrib import admin, messages
from diap.models.person import Person, PersonImage, PersonText


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
class ModeratorAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'middle_name')
    list_display = ['first_name', 'time_create', 'time_update', 'post_status']
    list_filter = ('time_create', 'post_status')
    ordering = ['time_update']
    inlines = [PersonImageInline, PersonTextInline]
    actions = ['make_published_person', 'make_unpublished_person', 'make_deleted_person' , 'delete_the_selected_files_to_a_personal_record']

    def get_queryset(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super(ModeratorAdmin, self).get_queryset(request, *args, **kwargs)
        else:
            return super(ModeratorAdmin, self).get_queryset(request, *args, **kwargs).filter(post_status='FOR_MODERATION').filter(moderator_take_task=f'{request.user.get_username}')
    
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

    @admin.action(description='Delete the selected files to a personal record')
    def delete_the_selected_files_to_a_personal_record(self, request, queryset):
        updated = queryset.update(moderator_take_task='not taken')
        self.message_user(request, ngettext(
            '%d The person has been successfully marked for moderation',
            updated,
        ) % updated, messages.SUCCESS)

# admin.site.unregister(Person)
# admin.site.register(Person, ModeratorAdmin)
# 
# 
