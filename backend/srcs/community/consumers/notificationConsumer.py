from channels.generic.websocket import AsyncWebsocketConsumer
from ..models import Friend, Messages
from django.db.models import Q
from asgiref.sync import sync_to_async
import json

class NotificationConsumer(AsyncWebsocketConsumer):

    active_connections = set()

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_group_name = f'notification'
        self.private_group_name = f'notification_{self.user.id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.private_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    @classmethod
    async def send_notification_to_all(cls, channel_layer, message, username='System'):
        """
        Broadcast a message to all WebSocket clients in the group.
        """
        await channel_layer.group_send(
            'notification',
            {
                'type': 'notification',
                'username': username,
                'message': message,
            }
        )

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