from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('is_authenticated/', views.is_authenticated, name='is_authenticated'),
]
