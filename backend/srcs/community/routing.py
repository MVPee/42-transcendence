from django.urls import path
from . import consumers
from . import notificationConsumers

websocket_urlpatterns = [
    path("ws/chat/<int:id>/", consumers.ChatConsumer.as_asgi()),
    path("ws/notification/", notificationConsumers.NotificationConsumer.as_asgi()),
]
