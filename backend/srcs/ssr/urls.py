from django.urls import path, re_path
from . import views
from .views import *

urlpatterns = [
    path('view/play/', PlayView.as_view(), name='play_view'),
    path('view/profile/', ProfileView.as_view(), name='profile_view'),
    path('view/settings/', SettingsView.as_view(), name='settings_view'),
    path('view/login/', LoginView.as_view(), name='login_view'),
    path('view/register/', RegisterView.as_view(), name='register_view'),
    path('view/community/', CommunityView.as_view(), name='community_view'),
    path('view/scoreboard/', ScoreboardView.as_view(), name='scoreboard_view'),
    path('view/waiting/<str:game_mode>/<str:queue_type>/', WaitingView.as_view(), name='waiting_view'),
    path('view/game/<str:game>/<str:mode>/<int:id>/', GameView.as_view(), name='game_view'),
    path('view/chat/<int:id>/', ChatView.as_view(), name='Chat_view'),

    path('friend/', FriendRequest.as_view(), name='friend_request'),
    path('block/', BlockRequest.as_view(), name='block_request'),
]
