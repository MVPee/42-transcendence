from django.urls import path

from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("offline/", views.offline_view, name="offline"),
    path("ai/", views.ai_view, name="offline"),
]