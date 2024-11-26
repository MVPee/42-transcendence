from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.utils import timezone
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.contrib.auth import get_user_model
import aiohttp, os, ssl, json

User = get_user_model()

class WaitingConsumer(AsyncWebsocketConsumer):
    rooms = {}

    DOMAIN = os.getenv('DOMAIN', 'localhost')
    API_KEY = os.getenv('API_KEY', None)

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async def connect(self):
        websocket_url = self.scope['path']
        self.GAME = websocket_url.split('/')[-3]
        self.MODE = websocket_url.split('/')[-2]
        self.user = self.scope['user']
        # print(f'waiting_{self.GAME}_{self.MODE}') #* DEBUG

        if self.GAME == 'private':
            friend = await self.get_friendship()
            if friend is None:
                self.close()
                return
            self.LEN_NEEDED = 2
        elif self.MODE == '1v1':
            self.LEN_NEEDED = 2
        elif self.MODE == '2v2':
            self.LEN_NEEDED = 4
        elif self.MODE == 'AI':
            self.LEN_NEEDED = 1
        elif self.MODE == 'tournament':
            self.LEN_NEEDED = 4

        self.room_group_name = f'waiting_{self.GAME}_{self.MODE}'

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
            if hasattr(self, 'room_group_name') and self.room_group_name in WaitingConsumer.rooms:
                WaitingConsumer.rooms[self.room_group_name].discard(self.user.username)
                if not WaitingConsumer.rooms[self.room_group_name]:
                    del WaitingConsumer.rooms[self.room_group_name]

                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

                # Update player list
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
            Redirect players in their game room after created it
        '''
        print(f'Redirecting players in {self.room_group_name}')

        connector = aiohttp.TCPConnector(ssl=self.ssl_context)

        player_usernames = list(WaitingConsumer.rooms.get(self.room_group_name, []))
        
        if self.GAME == 'private':
            self.GAME = 'pong'
            self.MODE = '1v1'
            url = f"https://{self.DOMAIN}/api/game/1v1/add/"
            data = {
                "title": 'private_1v1',
                "user1_username": player_usernames[0],
                "user2_username": player_usernames[1]
            }
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, json=data, headers={"X-API-KEY": self.API_KEY}) as response:
                    if response.status == 200: match = await response.json()
                    else:
                        self.close()
                        return
            
        if self.GAME == 'pong':
            if self.MODE == '1v1':
                url = f"https://{self.DOMAIN}/api/game/1v1/add/"
                data = {
                    "title": 'pong_1v1',
                    "user1_username": player_usernames[0],
                    "user2_username": player_usernames[1]
                }
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.post(url, json=data, headers={"X-API-KEY": self.API_KEY}) as response:
                        if response.status == 200: match = await response.json()
                        else:
                            self.close()
                            return
            elif self.MODE == '2v2':
                url = f"https://{self.DOMAIN}/api/game/2v2/add/"

                data = {
                    "title": 'pong_2v2',
                    "user1_username": player_usernames[0],
                    "user2_username": player_usernames[1],
                    "user3_username": player_usernames[2],
                    "user4_username": player_usernames[3]
                }
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.post(url, json=data, headers={"X-API-KEY": self.API_KEY}) as response:
                        if response.status == 200: match = await response.json()
                        else:
                            self.close()
                            return
            elif self.MODE == 'AI':
                url = f"https://{self.DOMAIN}/api/game/1v1/add/"
                data = {
                    "title": 'pong_ai',
                    "user1_username": player_usernames[0],
                    "user2_username": 'AI.'
                }
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.post(url, json=data, headers={"X-API-KEY": self.API_KEY}) as response:
                        if response.status == 200: match = await response.json()
                        else:
                            self.close()
                            return
            elif self.MODE == 'tournament':
                url = f"https://{self.DOMAIN}/api/game/2v2/add/"
                data = {
                    "title": 'tournament',
                    "user1_username": player_usernames[0],
                    "user2_username": player_usernames[1],
                    "user3_username": player_usernames[2],
                    "user4_username": player_usernames[3]
                }
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.post(url, json=data, headers={"X-API-KEY": self.API_KEY}) as response:
                        if response.status == 200: match = await response.json()
                        else:
                            self.close()
                            return
            else:
                self.close()
                return

        elif self.GAME == 'puissance4':
            if self.MODE == '1v1':
                url = f"https://{self.DOMAIN}/api/game/1v1/add/"
                data = {
                    "title": 'puissance4_1v1',
                    "user1_username": player_usernames[0],
                    "user2_username": player_usernames[1],
                }
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.post(url, json=data, headers={"X-API-KEY": self.API_KEY}) as response:
                        if response.status == 200: match = await response.json()
                        else:
                            self.close()
                            return
            else:
                self.close()
                return
        else:
            self.close()
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast_redirect",
                "game": self.GAME,
                "mode": self.MODE,
                "id": match['id']
            }
        )

    async def broadcast_redirect(self, event):
        '''
            Redirection broadcast message
        '''
        await self.send(text_data=json.dumps({
            "type": "redirect",
            "game": event["game"],
            "mode": event["mode"],
            "id": event["id"]
        }))

    async def get_friendship(self):
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        url = f"https://{self.DOMAIN}/api/friendship/{self.MODE}/"

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                if response.status == 200: data = await response.json()
                else: return None

        if data['status'] == False:
            return None

        if data['user1'] != self.user.id and data['user2'] != self.user.id:
            return None
        return data