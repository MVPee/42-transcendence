from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.cache import cache
import json
from .models import Match
from django.contrib.auth import get_user_model

User = get_user_model()

class GameConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['id']
        self.user = self.scope['user']
        self.room_group_name = f"game_{self.game_id}"

        # Add player to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Retrieve the match data asynchronously
        try:
            self.match = await sync_to_async(Match.objects.get)(id=self.game_id)
        
            # Fetch player names
            self.player1 = await sync_to_async(lambda: self.match.user1 if self.match.user1 else "Player1")()
            self.player2 = await sync_to_async(lambda: self.match.user2 if self.match.user2 else "Player2")()
            
            # Accept the WebSocket connection
            await self.accept()
            
            # Send player names to the client
            await self.send(text_data=json.dumps({
                "type": "player_info",
                "player1": self.player1.username,
                "player2": self.player2.username
            }))

        except Match.DoesNotExist:
            await self.close()

    async def receive(self, text_data):
        pass

    async def disconnect(self, close_code):
        # Only award points if points haven't been awarded yet for this game
        points_awarded_key = f"points_awarded_{self.game_id}"
        points_awarded = cache.get(points_awarded_key)

        if not points_awarded and hasattr(self, 'match'):
            if self.match.user1 == self.user:
                await self.set_points_to(2, 5)
                await self.set_win_to(2)
            elif self.match.user2 == self.user:
                await self.set_points_to(1, 5)
                await self.set_win_to(1)

            # Mark that points have been awarded in the cache
            cache.set(points_awarded_key, True, timeout=None)

            # Notify the remaining player to redirect
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "redirect_remaining_player",
                }
            )

        # Remove the player from the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        print(f"{self.user.username} disconnected")
    
    @sync_to_async
    def set_points_to(self, player, points):
        """Sets points for user1 and saves the match."""
        if (player == 1):
            self.match.user1_score = points
        elif (player == 2):
            self.match.user2_score = points
        self.match.save()

    @sync_to_async
    def set_win_to(self, player):
        """Sets win/defeat records for players and saves them."""
        if player == 1:
            self.match.user1.win += 1
            self.match.user2.defeat += 1
        elif player == 2:
            self.match.user2.win += 1
            self.match.user1.defeat += 1
        self.match.user1.save()
        self.match.user2.save()

    async def redirect_remaining_player(self, event):
        # Send a redirect message to the remaining player
        await self.send(text_data=json.dumps({
            "type": "redirect"
        }))
