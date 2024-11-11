import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.cache import cache
import json
from .models import Match
from django.contrib.auth import get_user_model

User = get_user_model()

class GameConsumer(AsyncWebsocketConsumer):

    PADDLE_SPEED = 4

    BALL_SPEED = 1

    HEIGHT = 400
    WIDTH = 600

    BALL_X = 300
    BALL_Y = 200

    BALL_HEIGHT = 5
    BALL_WIDTH = 5

    PADDLE_HEIGHT = 80
    PADDLE_WIDTH = 10

    PADDLE_MAX_HEIGHT = 400 - PADDLE_HEIGHT
    PADDLE_MIN_HEIGHT = 0

    async def connect(self):        
        self.game_id = self.scope['url_route']['kwargs']['id']
        self.user = self.scope['user']
        self.room_group_name = f"game_{self.game_id}"

        disconnect_key = f"player_disconnected_{self.game_id}"
        was_disconnected = cache.get(disconnect_key) == self.user.username

        if not cache.get(f"game_{self.game_id}_state"):
            cache.set(f"game_{self.game_id}_state", {
                'player1PaddleY': 200 - self.PADDLE_HEIGHT / 2,
                'player2PaddleY': 200 - self.PADDLE_HEIGHT / 2,
                'ball_x': self.BALL_X,
                'ball_y': self.BALL_Y,
                'ball_dx': self.BALL_SPEED,
                'ball_dy': self.BALL_SPEED,
                'paused': False,
            })

        cache.delete(disconnect_key)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        if was_disconnected:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_info",
                    "message": f"Player {self.user.username} has reconnected."
                }
                
            )

            # Resume the game
            game_state = cache.get(f"game_{self.game_id}_state")
            if game_state:
                game_state['paused'] = False
                cache.set(f"game_{self.game_id}_state", game_state)

        try:
            self.match = await sync_to_async(Match.objects.get)(id=self.game_id)
        
            self.player1 = await sync_to_async(lambda: self.match.user1 if self.match.user1 else "Player1")()
            self.player2 = await sync_to_async(lambda: self.match.user2 if self.match.user2 else "Player2")()
            
            await self.accept()
            
            await self.send(text_data=json.dumps({
                "type": "player_info",
                "player1": self.player1.username,
                "player2": self.player2.username
            }))

        except Match.DoesNotExist:
            await self.close()

        game_process_key = f"game_{self.game_id}_process_started"
        if not cache.get(game_process_key):
            cache.set(game_process_key, True)
            asyncio.create_task(self.gameProcess())

    async def gameProcess(self):
        while True:
            game_state = cache.get(f"game_{self.game_id}_state")
            if not game_state:
                break

            if game_state.get('paused'):
                await asyncio.sleep(0.1)
                continue

            ball_x = game_state['ball_x']
            ball_y = game_state['ball_y']
            ball_dx = game_state['ball_dx']
            ball_dy = game_state['ball_dy']

            ball_x += ball_dx
            ball_y += ball_dy

            # Handle collision with top and bottom walls
            if ball_y <= 0 or ball_y >= self.HEIGHT - self.BALL_HEIGHT:
                ball_dy *= -1

            # Handle collision with side walls (goals)
            if ball_x <= 0 or ball_x >= self.WIDTH - self.BALL_WIDTH:  # Assuming game width is 600
                # Ball went out of bounds, reset position
                ball_x = self.BALL_X
                ball_y = self.BALL_Y
                ball_dx *= -1  # Reverse X direction

            # Update game state
            game_state['ball_x'] = ball_x
            game_state['ball_y'] = ball_y
            game_state['ball_dx'] = ball_dx
            game_state['ball_dy'] = ball_dy

            cache.set(f"game_{self.game_id}_state", game_state)

            # Send updated ball position to clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_ball_position',
                    'ball_x': ball_x,
                    'ball_y': ball_y,
                }
            )

            # Sleep for 0.02 seconds (adjust as needed for smooth animation)
            await asyncio.sleep(0.02)

    async def update_ball_position(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update_ball_position',
            'ball_x': event['ball_x'],
            'ball_y': event['ball_y'],
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data["type"] == "movement" and (data["direction"] == 'up' or data["direction"] == 'down'):
            direction = data["direction"]

            game_state = cache.get(f"game_{self.game_id}_state")

            if self.user == self.player1:
                game_state['player1PaddleY'] += self.PADDLE_SPEED if direction == "down" else -self.PADDLE_SPEED
                game_state['player1PaddleY'] = max(self.PADDLE_MIN_HEIGHT, min(self.PADDLE_MAX_HEIGHT, game_state['player1PaddleY']))
            elif self.user == self.player2:
                game_state['player2PaddleY'] += self.PADDLE_SPEED if direction == "down" else -self.PADDLE_SPEED
                game_state['player2PaddleY'] = max(self.PADDLE_MIN_HEIGHT, min(self.PADDLE_MAX_HEIGHT, game_state['player2PaddleY']))
            
            cache.set(f"game_{self.game_id}_state", game_state)

            # Broadcast the movement to other players
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "player_movement",
                    "player": self.user.username,
                    "direction": direction,
                    "player1PaddleY": game_state['player1PaddleY'],
                    "player2PaddleY": game_state['player2PaddleY'],
                }
            )

    async def player_movement(self, event):
        # Send the movement data to WebSocket
        await self.send(text_data=json.dumps({
            "type": "player_movement",
            "player": event["player"],
            "direction": event["direction"],
            "player1PaddleY": event["player1PaddleY"],
            "player2PaddleY": event["player2PaddleY"],
        }))

    async def disconnect(self, close_code):
        points_awarded_key = f"points_awarded_{self.game_id}"
        points_awarded = cache.get(points_awarded_key)

        if not points_awarded and hasattr(self, 'match'):
            disconnect_key = f"player_disconnected_{self.game_id}"
            cache.set(disconnect_key, self.user.username, timeout=20)

            # Set the game to paused
            game_state = cache.get(f"game_{self.game_id}_state")
            if game_state:
                game_state['paused'] = True
                cache.set(f"game_{self.game_id}_state", game_state)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_info",
                    "message": f"Player {self.user.username} has disconnected. He have 15 seconds to reconnect."
                }
            )

            asyncio.create_task(self.wait_for_reconnection(disconnect_key, points_awarded_key))

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def wait_for_reconnection(self, disconnect_key, points_awarded_key):
        await asyncio.sleep(15)

        if cache.get(disconnect_key) == self.user.username:
            if self.match.user1 == self.user:
                await self.set_points_to(2, 5)
                await self.set_win_to(2)
            elif self.match.user2 == self.user:
                await self.set_points_to(1, 5)
                await self.set_win_to(1)

            cache.set(points_awarded_key, True, timeout=None)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "redirect_remaining_player",
                    "remaining_player": self.player2.username if self.match.user1 == self.user else self.player1.username
                }
            )

    @sync_to_async
    def set_points_to(self, player, points):
        if player == 1: self.match.user1_score = points
        elif player == 2: self.match.user2_score = points
        self.match.save()

    @sync_to_async
    def set_win_to(self, player):
        if player == 1:
            self.match.user1.win += 1
            self.match.user1.elo += 50
            self.match.user2.defeat += 1
            self.match.user2.elo -= 25
            if self.match.user2.elo < 0: self.match.user2.elo = 0
        elif player == 2:
            self.match.user2.win += 1
            self.match.user2.elo += 50
            self.match.user1.defeat += 1
            self.match.user1.elo -= 25
            if self.match.user1.elo < 0: self.match.user1.elo = 0
        self.match.user1.save()
        self.match.user2.save()

    async def redirect_remaining_player(self, event):
        if event["remaining_player"] == self.user.username:
            await self.send(text_data=json.dumps({
                "type": "redirect"
            }))

    async def send_info(self, event):
        await self.send(text_data=json.dumps({
            "type": "info",
            "info": event["message"]
        }))