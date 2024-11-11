from django.urls import path

from . import gameConsumers
from . import waitingConsumers

websocket_urlpatterns = [
    path("ws/waiting/<str:game_mode>/<str:queue_type>/", waitingConsumers.WaitingConsumer.as_asgi()),
    path("ws/game/<int:id>/", gameConsumers.GameConsumer.as_asgi()),
]
