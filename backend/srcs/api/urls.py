from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('view/home/', HomeView.as_view(), name='home_view'),
    path('view/profile/', ProfileView.as_view(), name='profile_view'),
    path('view/login/', LoginView.as_view(), name='login_view'),
    path('view/register/', RegisterView.as_view(), name='register_view'),

    path('is_authenticated/', views.is_authenticated, name='is_authenticated'),
]
