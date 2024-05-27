from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        labels = {
            'username': _("Користувач"),
            'password1': _("Пароль"),
            'password2': _("Підтвердження пароля")
        }

class LoginForm(forms.Form):
    username = forms.CharField(label=_("Користувач"))
    password = forms.CharField(widget=forms.PasswordInput, label=_("Пароль"))