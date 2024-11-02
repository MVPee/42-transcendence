from django.urls import path
from .views import HomeView, ProfileView, LoginView

urlpatterns = [
    path('view/home/', HomeView.as_view(), name='home_view'),
    path('view/profile/', ProfileView.as_view(), name='profile_view'),
    path('view/login/', LoginView.as_view(), name='login_view'),
]
