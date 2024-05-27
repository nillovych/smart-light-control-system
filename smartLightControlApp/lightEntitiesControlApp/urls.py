from django.urls import path
from . import views

urlpatterns = [
    path('<str:entity_id>/', views.light_control, name='light_control')
]
