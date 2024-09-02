from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class ClientCreateForm(UserCreationForm):
    username = forms.CharField(label=_('Логін'), widget=forms.TextInput(
        attrs={
            "placeholder": _("Ваш логін"), "class": "text-center form-control validate"
        }), error_messages = {
            'invalid': _('Некоректне ім\'я користувача. Ім\'я користувача може містити в собі тільки букви, цифри та символи @/./+/-/_.'),
            'unique': _('Ім\'я користувача вже зайнято.')
        })
    email = forms.EmailField(label='Email', widget=forms.TextInput(
        attrs={
            "placeholder": _("Ваша електронна пошта (example@example.com)"),
            "class": "text-center form-control validate"
        }), error_messages={'invalid': _('Неправільний формат адреси електронної пошти.')})
    password1 = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput(
        attrs={
            "placeholder": _("Створіть пароль"),
            "class": "text-center form-control validate"
        }))
    password2 = forms.CharField(label=_('Повторіть пароль'), widget=forms.PasswordInput(
        attrs={
            "placeholder": _("Повторіть пароль"),
            "class": "text-center form-control validate"
        }))
    ######
    error_messages = {
        'password_mismatch': _('Паролі не співпадають.'),
        'password_too_short': _('Пароль повинен містити не менше 8 символів.'),
        'password_common_words': _('Пароль містить слова, що часто використовуються. Будь-ласка, використовуйте складніший пароль.'),
        'password_too_similar': _('Пароль схожий на ім\'я користувача.'),
        'password_entirely_numeric': _('Пароль не може складатись тільки з цифр.')
    }

    def clean_password2(self):
        username = self.cleaned_data.get('username')
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if len(password2) < 8:
            raise forms.ValidationError(
                self.error_messages['password_too_short'],
                code='password_too_short',
            )

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        if username and password1 and username.lower() in password1.lower():
            raise forms.ValidationError(
               self.error_messages['password_too_similar'],
                code='password_too_similar',
            )
        if password1.isdigit():
            raise forms.ValidationError(
                self.error_messages['password_entirely_numeric'],
                code='password_entirely_numeric',
            )
        
        # with open('common-passwords.txt', 'r') as f: #add file common-passwords.txt to git
        #     common_passwords = {line.strip() for line in f.readlines()}

        # if any(word in password2.lower() for word in common_passwords):
        #     raise forms.ValidationError(
        #         self.error_messages['password_common_words'],
        #         code='password_common_words',
        #     )

        return password2


class LogInClientForm(AuthenticationForm):
    username = forms.CharField(label=_('Логін'), widget=forms.TextInput(
        attrs={
            "placeholder": _("Введіть логін"), "class": "text-center form-control validate"
        }))
    password = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput(
        attrs={
            "placeholder": _("Введіть пароль"),
            "class": "text-center form-control validate"
        }))
    error_messages = {
        'invalid_login': _("Неправильне ім'я користувача або пароль."),
        'inactive': _("Цей аккаунт неактивний."),
    }

