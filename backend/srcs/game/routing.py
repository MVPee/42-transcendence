from django.urls import path
from .consumers.waitingConsumer import WaitingConsumer
from .consumers.game1v1Consumer import Game1v1Consumer
from .consumers.game2v2Consumer import Game2v2Consumer
from .consumers.gameAIConsumer import GameAIConsumer
from .consumers.puissance4Consumer import Puissance4Consumer
from .consumers.gameTournamentConsumer import GameTournamentConsumer

websocket_urlpatterns = [
    path("ws/waiting/<str:game_mode>/<str:queue_type>/", WaitingConsumer.as_asgi()),
    path("ws/waiting/private/<int:friend_id>/", WaitingConsumer.as_asgi()),
    path("ws/game/pong/1v1/<int:id>/", Game1v1Consumer.as_asgi()),
    path("ws/game/pong/AI/<int:id>/", GameAIConsumer.as_asgi()),
    path("ws/game/pong/2v2/<int:id>/", Game2v2Consumer.as_asgi()),
    path("ws/game/pong/tournament/<int:id>/", GameTournamentConsumer.as_asgi()),
    path("ws/game/puissance4/1v1/<int:id>/", Puissance4Consumer.as_asgi()),
]
