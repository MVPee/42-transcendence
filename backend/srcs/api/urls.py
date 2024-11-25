from django.urls import path
import srcs.api.views.community as community
import srcs.api.views.user as user
import srcs.api.views.others as others

urlpatterns = [
    path('check_api_key/', others.check_api_key, name='check_api_key'),

    path('is_authenticated/', user.is_authenticated, name='is_authenticated'),
    path('users/<int:id>/', user.get_user_by_id, name='get_user_by_id'),
    path('users/<str:username>/', user.get_user_by_username, name='get_user_by_username'),
    path('logout/', user.logout, name='logout'),
    path('login/', user.login, name='login'),
    path('register/', user.register, name='register'),
    path('settings/', user.settings, name='change_settings'),

    path('check_friendship/<int:user1>/<int:user2>/', community.check_friendship, name="validate_friendship"),
    path('friendship/<int:pk>/', community.get_friendship, name="get_friendship"),
    path('friendship/<int:user1>/<int:user2>/', community.get_friendship_by_users, name="get_friendship_by_users"),
    path('message/add/', community.add_message, name="add_message"),
    path('block/', community.block, name='block_request'),
    path('has_blocked/<int:user1_id>/<int:user2_id>/', community.has_blocked, name='has_blocked'),
    path('friend/', community.friend, name='friend_request'),
]
