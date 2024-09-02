import os

from django import template

from diap.models.person import Person, PersonImage
from django.contrib.auth.models import User, Group
register = template.Library()


@register.simple_tag(name='check_image')
def check_image(val: Person = None):
    if val:
        images = val.images.all()
        for i in images:
            if i.main_image and i.image:
                return i.image.url
        try:
            if images.first().image:
                return images.first().image.url
        except:
            return 'https://poternet.site/media/photos/2023/06/19/photo_2023-06-08_18-42-34_CVoKIG3.jpg'
    return 'https://poternet.site/media/photos/2023/06/19/photo_2023-06-08_18-42-34_CVoKIG3.jpg'


@register.simple_tag(name='check_detail_image')
def check_detail_image(val: PersonImage.objects.all() = None):
    if val:
        for i in val:
            if i.main_image:
                return i.image.url
        try:
            if val.first().image:
                return val.first().image.url
        except:
            return 'https://poternet.site/media/photos/2023/06/19/photo_2023-06-08_18-42-34_CVoKIG3.jpg'
    return 'https://poternet.site/media/photos/2023/06/19/photo_2023-06-08_18-42-34_CVoKIG3.jpg'


@register.simple_tag(name='check_lang_url')
def check_detail_image(url: str, val: str):
    if url:
        response = url.split('/')
        response = "/".join(response[2:])
        return os.environ.get("CSRF_TRUSTED_ORIGINS", default='https://poternet.site')+'/'+val+response
    return ''

@register.simple_tag(name='get_group')
def get_user_group(obj):
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



