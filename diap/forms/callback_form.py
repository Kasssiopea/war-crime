from diap.models.person import Person, PersonImage
from django.db import models
from diap.models.choices import (
    PersonTypeSocialNetworkChoices,
    StatusPersonChoices,
    StatusPersonPostChoices,
    StatusPersonPostPublished, ArmyRangChoices, ArmyTypeChoices, DateMonth, DateDay,
)
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.forms import ModelForm

from diap.models.callback import CallBack

from django import forms

from django.utils.translation import gettext_lazy as _
class CallBackForm(ModelForm):
    class Meta:
        model = CallBack
        fields = ["title", "text"]
        widgets = {
            'title': forms.TextInput(attrs={'style': 'margin-bottom: 25px; vertical-align: center;'}), 
            'text': forms.Textarea(attrs={'class': 'materialize-textarea', 'style': 'margin-bottom: 15px; vertical-align: center;padding: 10px; line-height: 1.5em; border: 1px solid #9e9e9e; border-radius: 5px; resize: vertical; min-height: 150px;'}),
        }

class NewPerson(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["birthday_month"].initial = '00'
        self.fields["birthday_day"].initial = '00'
        self.fields["type_of_army_choice"].initial = '00'
        self.fields["rank_choice"].initial = '00'
        self.fields["data_when_accident_day"].initial = '00'
        self.fields["data_when_accident_month"].initial = '00'
        self.fields["place_of_rip_date_month"].initial = '00'
        self.fields["place_of_rip_date_day"].initial = '00'

    class Meta:
        model = Person
        fields = [
        "last_name",
        "first_name",
        "middle_name",
        "birthday_year",
        "birthday_month",
        "birthday_day",
        "citizenship",
        "passport",
        "individual_identification_number",
        "place_of_birthday",
        "place_of_living",
        "type_of_army_choice",
        "rank_choice",
        "job_title",
        "military_unit",
        "military_from",
        "place_where_accident",
        "data_when_accident_year",
        "data_when_accident_month",
        "data_when_accident_day",
        "place_of_rip",
        "place_of_rip_date_year",
        "place_of_rip_date_month",
        "place_of_rip_date_day",
        "additional_info",
        "source"]
        widgets = {
            "last_name": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;', 'class': 'form-control'}), 
            "first_name": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;', 'class': 'form-control'}),
            "middle_name": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;', 'class': 'form-control'}),
            "birthday_year": forms.NumberInput(attrs={'class': 'form-control', 'max': '2025', 'min': '1950', 'style': 'vertical-align: center;'}),
            "birthday_month": forms.Select(choices=DateMonth, attrs={'class': 'browser-default', 'style': 'vertical-align: center; border: 0; border-bottom: 1px solid #9e9e9e;'}),
            "birthday_day": forms.Select(choices=DateDay, attrs={'class': 'browser-default', 'style': 'vertical-align: center; border: 0; border-bottom: 1px solid #9e9e9e;'}),
            "citizenship": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;'}),
            "passport": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;'}),
            "individual_identification_number": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;'}),
            "place_of_birthday": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;'}),
            "place_of_living": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;'}),
            "type_of_army_choice": forms.Select(choices=ArmyTypeChoices, attrs={'class': 'browser-default', 'style': 'margin-bottom: 30px; vertical-align: center; border: 0; border-bottom: 1px solid #9e9e9e;'}),
            "rank_choice": forms.Select(choices=ArmyRangChoices, attrs={'class': 'browser-default', 'style': 'margin-bottom: 30px; vertical-align: center; border: 0; border-bottom: 1px solid #9e9e9e;'}),
            "job_title": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;'}),
            "military_unit": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;'}),
            "military_from": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;'}),
            "place_where_accident": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;'}),
            "data_when_accident_year": forms.NumberInput(attrs={'class': 'form-control', 'max': '2025', 'min': '1950', 'style': 'vertical-align: center;'}),
            "data_when_accident_month": forms.Select(choices=DateMonth, attrs={'class': 'browser-default', 'style': 'vertical-align: center; border: 0; border-bottom: 1px solid #9e9e9e;'}),
            "data_when_accident_day": forms.Select(choices=DateDay, attrs={'class': 'browser-default', 'style': 'vertical-align: center; border: 0; border-bottom: 1px solid #9e9e9e;'}),
            "place_of_rip": forms.TextInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center;'}),
            "place_of_rip_date_year": forms.NumberInput(attrs={'class': 'form-control', 'max': '2025', 'min': '1950', 'style': 'vertical-align: center;'}),
            "place_of_rip_date_month": forms.Select(choices=DateMonth, attrs={'class': 'browser-default', 'style': 'vertical-align: center; border: 0; border-bottom: 1px solid #9e9e9e;'}),
            "place_of_rip_date_day": forms.Select(choices=DateDay, attrs={'class': 'browser-default', 'style': 'vertical-align: center; border: 0; border-bottom: 1px solid #9e9e9e;'}),
            "additional_info": forms.Textarea(attrs={'class': 'materialize-textarea', 'style': 'vertical-align: center;padding: 10px; line-height: 1.5em; border: 1px solid #9e9e9e; border-radius: 5px; resize: vertical; min-height: 45px;'}),
            "source": forms.Textarea(attrs={'class': 'materialize-textarea', 'style': 'vertical-align: center;padding: 10px; line-height: 1.5em; border: 1px solid #9e9e9e; border-radius: 5px; resize: vertical; min-height: 45px;'})
        }

class NewPersonImg(ModelForm):
    class Meta:
        model = PersonImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'style': 'margin-bottom: 30px; vertical-align: center; width: 100%;', 'class': 'form-control', 'required': False}),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].validators.append(FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', 'jfif', 'bmp', 'gif', 'svg', 'png', 'webp',
            'svgz', 'jpg', 'jpeg', 'ico', 'xbm', 'dib', 'pjp', 'apng', 'tif', 'pjpeg', 'avif'], message=_("Недопустимий формат файла.")))
    
    def clean_image(self):
        cleaned_data = super().clean()
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 3 * 1024 * 1024:
                raise forms.ValidationError(_("Розмір файла повинен бути не більше 3 Мб."))
            return image

