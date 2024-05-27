from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('lights/<str:entity_id>/', views.light_control, name='light_control'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
]