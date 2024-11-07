from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('view/home/', HomeView.as_view(), name='home_view'),
    path('view/profile/', ProfileView.as_view(), name='profile_view'),
    path('view/login/', LoginView.as_view(), name='login_view'),
    path('view/logout/', LogoutView.as_view(), name='logout_view'),
    path('view/register/', RegisterView.as_view(), name='register_view'),
    path('view/community/', CommunityView.as_view(), name='community_view'),
    path('view/scoreboard/', ScoreboardView.as_view(), name='scoreboard_view'),

    path('view/websocket/', WebSocketView.as_view(), name='websocket_view'),
]
