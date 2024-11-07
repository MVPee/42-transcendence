from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.base_view, name='base'),
    re_path(r'^(?!static|admin|ssr|api).*/?$', views.base_view, name='base'),
]