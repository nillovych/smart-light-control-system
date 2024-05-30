from django.urls import path

from .views import user_profile, try_connect, update_consent, train_models, ai_control_enabled

urlpatterns = [
    path('', user_profile, name='profile'),
    path('try-connect/', try_connect, name='try_connect'),
    path('update_consent/', update_consent, name='update_consent'),
    path('ai_control_enabled/', ai_control_enabled, name='ai_control_enabled'),
    path('train_models/', train_models, name='train_models'),
]
