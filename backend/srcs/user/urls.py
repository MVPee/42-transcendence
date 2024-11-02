from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^(?:home|profile|login)?$', views.base_view, name='base'),
]