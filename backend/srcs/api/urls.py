from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('is_authenticated/', views.is_authenticated, name='is_authenticated'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('check_api_key/', views.check_api_key, name='check_api_key'),
]
