from django.urls import path

from . import views

app_name='chat'

urlpatterns = [
    path("", views.index_view, name="index"),
    path('send_friend_request/', views.send_friend_request, name='send_friend_request'),
    path('send_friend_request/<int:user_id>', views.send_friend_request_by_id, name='send_friend_request'),
    path('respond_friend_request/<int:friend_request_id>/', views.respond_friend_request, name='respond_friend_request'),
    path('unfriend/<int:friendship_id>/', views.unfriend, name='unfriend'),
    path('block/', views.block, name='block'),
    path('block/<int:user_id>', views.block_by_id, name='block'),
    path('unblock/<int:blocked_id>/', views.unblock, name='unblock'),
    path('private/<int:friendship_id>/', views.private_chat, name='private_chat'),
]