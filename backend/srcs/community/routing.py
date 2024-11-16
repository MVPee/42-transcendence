from django.urls import path
from .consumers import chatConsumer
from .consumers import notificationConsumer

websocket_urlpatterns = [
    path("ws/chat/<int:id>/", chatConsumer.ChatConsumer.as_asgi()),
    path("ws/notification/", notificationConsumer.NotificationConsumer.as_asgi()),
]
