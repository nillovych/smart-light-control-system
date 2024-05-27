from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=300)
    company_domain = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
