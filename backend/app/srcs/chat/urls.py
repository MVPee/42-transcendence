from django.urls import path

from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("global/", views.global_chat_view, name="global_chat"),
]