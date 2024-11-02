from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^(?:home|profile|login)?$', views.base_view, name='base'),
    path('api/get_html/<str:page>/', views.get_html, name='get_html'),
]