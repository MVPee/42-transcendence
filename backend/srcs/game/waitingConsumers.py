from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.utils import timezone
from asgiref.sync import sync_to_async
from .models import Match
from django.contrib.auth import get_user_model

User = get_user_model()

class WaitingConsumer(AsyncWebsocketConsumer):
    players = set()  # Track all connected players

    async def connect(self):
        self.room_group_name = 'waiting_pong'
        self.user = self.scope['user']

        if self.user.is_authenticated:
            # Add user to the set of connected players
            WaitingConsumer.players.add(self.user.username)

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Send the updated list of all players to all clients
            await self.send_player_list_to_all()

            # print(f"Number of connected players: {len(WaitingConsumer.players)}") #*DEBUG
            if (len(WaitingConsumer.players) == 2):
                await self.redirect_all_players()

        else: self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            # Remove user from the set when they disconnect
            WaitingConsumer.players.discard(self.user.username)

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            # Update all clients with the new player list
            await self.send_player_list_to_all()

    async def receive(self, text_data):
        pass

    async def send_player_list_to_all(self):
        # Broadcast the updated player list to all clients in the waiting room
        player_list = list(WaitingConsumer.players)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast_player_list",
                "players": player_list,
            }
        )

    async def broadcast_player_list(self, event):
        # Send the player list to each connected client
        await self.send(text_data=json.dumps({
            "type": "player_list",
            "players": event["players"]
        }))

    async def redirect_all_players(self):
        print('Redirection of players')

        player_usernames = list(WaitingConsumer.players)
        user1 = await sync_to_async(User.objects.get)(username=player_usernames[0])
        user2 = await sync_to_async(User.objects.get)(username=player_usernames[1])

        match = await sync_to_async(Match.objects.create)(user1=user1, user2=user2, created_at=timezone.now())

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast_redirect",
                "id": match.id
            }
        )

    async def broadcast_redirect(self, event):
        # Send a redirect message to each connected client
        await self.send(text_data=json.dumps({
            "type": "redirect",
            "id": event["id"]
        }))