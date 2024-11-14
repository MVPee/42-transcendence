import json
import asyncio
from .models import Match
from django.db.models import Q
from django.core.cache import cache
from asgiref.sync import sync_to_async
from srcs.community.models import Friend
from channels.generic.websocket import AsyncWebsocketConsumer

class Puissance4Consumer(AsyncWebsocketConsumer):

    YELLOW = 0
    RED = 0

    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['id']
        self.room_group_name = f'game_{self.game_id}_puissance4'
        self.user = self.scope['user']

        disconnect_key = f"player_disconnected_{self.game_id}"
        was_disconnected = cache.get(disconnect_key) == self.user.username

        if not cache.get(f"game_{self.game_id}_puissance4_state"):
            cache.set(f"game_{self.game_id}_puissance4_state", {
                'table': [[None for _ in range(6)] for _ in range(7)],
                'turn': 'yellow',
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
            game_state = cache.get(f"game_{self.game_id}_1v1_state")
            if game_state:
                game_state['paused'] = False
                cache.set(f"game_{self.game_id}_1v1_state", game_state)
        
        try:
            self.match = await sync_to_async(Match.objects.get)(id=self.game_id)
        
            self.player1 = await sync_to_async(lambda: self.match.user1 if self.match.user1 else "Player1")()
            self.player2 = await sync_to_async(lambda: self.match.user2 if self.match.user2 else "Player2")()
            
            await self.accept()
        except Match.DoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        points_awarded_key = f"points_awarded_{self.game_id}"
        points_awarded = cache.get(points_awarded_key)

        if not points_awarded and hasattr(self, 'match'):
            disconnect_key = f"player_disconnected_{self.game_id}"
            cache.set(disconnect_key, self.user.username, timeout=20)

            # Set the game to paused
            game_state = cache.get(f"game_{self.game_id}_1v1_state")
            if game_state:
                game_state['paused'] = True
                cache.set(f"game_{self.game_id}_1v1_state", game_state)

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

        #? Protection if the match is finish
        if await self.check_win() == 0:
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
                        }
                )

    async def receive(self, text_data):
        print(text_data)
        if text_data.isnumeric() and int(text_data) >= 0 and int(text_data) <= 7:
            column = int(text_data)
            game_state = cache.get(f"game_{self.game_id}_puissance4_state")
            if game_state['turn'] == 'yellow' and self.user == self.player1 and game_state['table'][column][0] is None:
                for row in range(5, -1, -1):
                    if game_state['table'][column][row] is None:
                        game_state['table'][column][row] = self.YELLOW
                        game_state['turn'] = 'red'
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "send_color",
                                "column": column ,
                                "row": row,
                                "color": 'yellow',
                            }
                        )
                        break

            elif game_state['turn'] == 'red' and self.user == self.player2 and game_state['table'][column][0] is None:
                for row in range(5, -1, -1):
                    if game_state['table'][column][row] is None:
                        game_state['table'][column][row] = self.RED
                        game_state['turn'] = 'yellow'
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "send_color",
                                "column": column ,
                                "row": row,
                                "color": 'red',
                            }
                        )
                        break

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_turn",
                    "message": f"{game_state['turn']} turn."
                }
            )

            cache.set(f"game_{self.game_id}_puissance4_state", game_state)

    async def send_color(self, event):
        await self.send(text_data=json.dumps({
            "type": "color",
            "column": event["column"],
            "row": event["row"],
            "color": event["color"]
        }))

    async def send_info(self, event):
        await self.send(text_data=json.dumps({
            "type": "info",
            "info": event["message"]
        }))

    async def send_turn(self, event):
        await self.send(text_data=json.dumps({
            "type": "turn",
            "turn": event["message"]
        }))

    @sync_to_async
    def set_points_to(self, player, points):
        if player == 1: 
            self.match.user1_score = points
        elif player == 2: 
            self.match.user2_score = points
        self.match.save()

    @sync_to_async
    def check_win(self):
        if self.match.user1_score >= 5:
            return 1
        elif self.match.user2_score >= 5:
            return 2
        return 0
    
    @sync_to_async
    def set_win_to(self, player):
        if player == 1:
            self.match.user1.elo += 50
            self.match.user2.elo -= 25
            if self.match.user2.elo < 0: self.match.user2.elo = 0
        elif player == 2:
            self.match.user2.elo += 50
            self.match.user1.elo -= 25
            if self.match.user1.elo < 0: self.match.user1.elo = 0
        self.match.user1.save()
        self.match.user2.save()

    async def redirect_remaining_player(self, event):
        await self.send(text_data=json.dumps({
            "type": "redirect"
        }))