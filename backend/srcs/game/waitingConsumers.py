from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.utils import timezone
from asgiref.sync import sync_to_async
from .models import Match
from django.contrib.auth import get_user_model

User = get_user_model()

class WaitingConsumer(AsyncWebsocketConsumer):
    rooms = {}

    async def connect(self):
        websocket_url = self.scope['path']
        self.GAME = websocket_url.split('/')[-3]
        self.MODE = websocket_url.split('/')[-2]
        # print(f'waiting_{self.GAME}_{self.MODE}') #* DEBUG

        if self.MODE == '1v1':
            self.LEN_NEEDED = 2
        elif self.MODE == '2v2':
            self.LEN_NEEDED = 4
        elif self.MODE == 'AI':
            self.LEN_NEEDED = 1

        self.room_group_name = f'waiting_{self.GAME}_{self.MODE}'
        self.user = self.scope['user']

        if self.user.is_authenticated:
            #? Create the room
            if self.room_group_name not in WaitingConsumer.rooms:
                WaitingConsumer.rooms[self.room_group_name] = set()

            #? Add user to the room
            WaitingConsumer.rooms[self.room_group_name].add(self.user.username)

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            #? MAJ of the player list
            await self.send_player_list_to_all()

            # print(f"Number of connected players in {self.room_group_name}: {len(WaitingConsumer.rooms[self.room_group_name])}") #*DEBUG
            if len(WaitingConsumer.rooms[self.room_group_name]) == self.LEN_NEEDED:
                await self.redirect_all_players()

        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            if self.room_group_name in WaitingConsumer.rooms:
                WaitingConsumer.rooms[self.room_group_name].discard(self.user.username)
                if not WaitingConsumer.rooms[self.room_group_name]:
                    del WaitingConsumer.rooms[self.room_group_name]

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            #? MAJ of the player list
            await self.send_player_list_to_all()

    async def send_player_list_to_all(self):
        '''
            Send player list of the room
        '''
        player_list = list(WaitingConsumer.rooms.get(self.room_group_name, set()))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast_player_list",
                "players": player_list,
            }
        )

    async def broadcast_player_list(self, event):
        await self.send(text_data=json.dumps({
            "type": "player_list",
            "players": event["players"]
        }))

    async def redirect_all_players(self):
        '''
            Redirect players in their game room
        '''
        print(f'Redirecting players in {self.room_group_name}')

        player_usernames = list(WaitingConsumer.rooms.get(self.room_group_name, []))
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
        '''
            Redirection broadcast message
        '''
        await self.send(text_data=json.dumps({
            "type": "redirect",
            "id": event["id"]
        }))
