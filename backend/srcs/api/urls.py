from django.urls import path
import srcs.api.views.community as community
import srcs.api.views.user as user
import srcs.api.views.others as others

urlpatterns = [
    path('check_api_key/', others.check_api_key, name='check_api_key'),

    path('is_authenticated/', user.is_authenticated, name='is_authenticated'),
    path('logout/', user.logout, name='logout'),
    path('login/', user.login, name='login'),
    path('register/', user.register, name='register'),
    path('settings/', user.settings, name='change_settings'),

    path('check_friendship/<int:user1>/<int:user2>/', community.check_friendship, name="validate_friendship"),
    path('friendship/<int:pk>/', community.get_friendship, name="get_friendship"),
    path('message/add/', community.add_message, name="add_message"),
    path('block/', community.block, name='block_request'),
    path('friend/', community.friend, name='friend_request'),
]
