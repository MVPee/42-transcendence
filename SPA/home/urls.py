from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),  # Vue pour charger base.html
    path('home/', views.home_view, name='home'),  # Chargé dynamiquement via Ajax
    path('about/', views.about_view, name='about'),  # Chargé dynamiquement via Ajax
]