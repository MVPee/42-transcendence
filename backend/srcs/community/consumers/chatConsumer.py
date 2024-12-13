from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db.models import Q
import aiohttp
import json
import ssl
import os

class ChatConsumer(AsyncWebsocketConsumer):

    DOMAIN = os.getenv('DOMAIN', 'localhost')
    API_KEY = os.getenv('API_KEY', None)

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async def connect(self):

        self.id = self.scope['url_route']['kwargs']['id']
        self.room_group_name = f'chat_{self.id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return

        self.friendship = await self.get_friendship()
        if not self.friendship:
            await self.close()
            return

        self.friend_user = await self.get_friend_user()
        if not self.friend_user:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            if len(message) > 100  or len(message) == 0:
                return
            username = self.user.username
            await self.channel_layer.group_send(self.room_group_name,{
                'type': 'chatroom_message',
                'username': username,
                'message': message,
            })
            await self.add_chatdb(message)
        except json.JSONDecodeError:
            print(text_data)

    async def send_notification_to_friend(self, message):
        """
        Send a notification to the other user in the friendship.
        """
        
        await self.channel_layer.group_send(
            f'notification_{self.friend_user}',  # Friend's private notification group
            {
                'type': 'notification',
                'username': self.user.username,
                'message': f"{message}",
            }
        )

    @sync_to_async
    def get_friend_user(self):
        """
        Get the other user in the friendship.
        """
        if self.friendship["user1"] == self.user.id:
            return self.friendship["user2"]
        return self.friendship["user1"]
        
    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'username': username,
            'message': message,
        }))

    async def add_chatdb(self, message):
        if len(message) <= 100:
            url = f"http://{self.DOMAIN}:8000/api/message/add/"
            payload = {
                "friendship": self.friendship['id'],
                "sender": self.user.id,
                "message": message,
                "X-API-KEY": self.API_KEY
            }

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, json=payload, headers={"X-API-KEY": self.API_KEY}) as response:
                    if response.status == 201: await self.send_notification_to_friend(message)
                    # else: print(f"Failed to save message. Status code: {response.status}") #* DEBUG
                    pass

    async def get_friendship(self):
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        url = f"http://{self.DOMAIN}:8000/api/friendship/{self.id}/"

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                if response.status == 200: data = await response.json()
                else: return None

        if data['status'] == False:
            return None

        if data['user1'] != self.user.id and data['user2'] != self.user.id:
            return None
        return data

    async def notification(self, event):
        """
        Handle broadcast notifications sent to the group.
        """
        username = event.get('username', 'System')

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'username': username,
            'message': event['message'],
        }))