from django.contrib.auth.models import User
from django.db import models


class LightingEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    lamp_id = models.CharField(max_length=255)
    brightness = models.IntegerField(null=True, blank=True)
    color_r = models.IntegerField(null=True, blank=True)
    color_g = models.IntegerField(null=True, blank=True)
    color_b = models.IntegerField(null=True, blank=True)
    state = models.BooleanField()

    def __str__(self):
        return f"{self.state} - {self.lamp_id} - {self.timestamp}"


class ModelsStorage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    scaler = models.BinaryField()
    state_model = models.BinaryField()
    brightness_model = models.BinaryField()
    color_r_model = models.BinaryField()
    color_g_model = models.BinaryField()
    color_b_model = models.BinaryField()
