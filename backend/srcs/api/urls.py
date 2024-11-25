from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('check_api_key/', views.check_api_key, name='check_api_key'),
    path('is_authenticated/', views.is_authenticated, name='is_authenticated'),

    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),

    path('check_friendship/<int:user1>/<int:user2>/', views.check_friendship, name="validate_friendship"),
    path('friendship/<int:pk>/', views.get_friendship, name="get_friendship"),
    path('message/add/', views.add_message, name="add_message"),
]
