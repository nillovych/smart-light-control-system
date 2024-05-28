from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=300)
    company_domain = models.CharField(max_length=100)
    consent_for_data_collection = models.BooleanField(default=False)
    ai_control_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
