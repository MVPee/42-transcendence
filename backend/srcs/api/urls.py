from django.urls import path
import srcs.api.views.community as community
import srcs.api.views.user as user
import srcs.api.views.others as others
import srcs.api.views.game as game

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

    path('game/1v1/', game.all_1v1_game, name='all_1v1_game'),
    path('game/2v2/', game.all_2v2_game, name='all_2v2_game'),
    path('game/tournament/', game.all_tournament_game, name='all_tournament_game'),
    path('game/1v1/<int:id>/', game.get_1v1_game, name='get_1v1_game'),
    path('game/2v2/<int:id>/', game.get_2v2_game, name='get_2v2_game'),
    path('game/tournament/<int:id>/', game.get_tournament_game, name='get_tournament_game'),

    path('game/1v1/add/', game.create_1v1_game, name='create_1v1_game'),
    path('game/2v2/add/', game.create_2v2_game, name='create_2v2_game'),
]
