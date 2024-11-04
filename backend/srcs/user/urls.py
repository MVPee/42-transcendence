from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.base_view, name='base'),
    re_path(r'^(?:home|scoreboard|profile|login|register|logout|community|websocket)/?$', views.base_view, name='base'),
]