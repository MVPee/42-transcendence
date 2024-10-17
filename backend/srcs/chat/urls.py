from django.urls import path

from . import views

app_name='chat'

urlpatterns = [
    path("", views.index_view, name="index"),
    path("global/", views.global_chat_view, name="global_chat"),
    path('send_friend_request/', views.send_friend_request, name='send_friend_request'),
    path('respond_friend_request/<int:friend_request_id>/', views.respond_friend_request, name='respond_friend_request'),
    path('unfriend/<int:friendship_id>/', views.unfriend, name='unfriend'),
    path('block/', views.block, name='block'),
    path('unblock/<int:blocked_id>/', views.unblock, name='unblock'),
    path('private/<int:friendship_id>/', views.private_chat, name='private_chat'),
]