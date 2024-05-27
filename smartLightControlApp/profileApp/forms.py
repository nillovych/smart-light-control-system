from django import forms
from .models import UserProfile
from django.utils.translation import gettext_lazy as _

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['access_token', 'company_domain']
        labels = {
            'access_token': _("Токен доступу"),
            'company_domain': _("Домен компанії")
        }