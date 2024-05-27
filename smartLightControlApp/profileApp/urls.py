from django.urls import path

from .views import user_profile, try_connect

urlpatterns = [
    path('', user_profile, name='profile'),
    path('try-connect/', try_connect, name='try_connect'),

]
