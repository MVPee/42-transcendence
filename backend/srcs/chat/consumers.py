from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth import get_user_model
import redis.asyncio as redis
from .models import *
from channels.db import database_sync_to_async
from srcs.user.models import CustomUser as User


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.friendship_id = self.scope['url_route']['kwargs']['friendship_id']
        self.friendship = await self.get_friendship_if_part_of()

        # Check if the user is part of this friendship
        if not self.friendship:
            await self.close()
            return

        # Determine the friend (the other user)
        if self.friendship.user1 == self.user:
            self.friend = self.friendship.user2
        else:
            self.friend = self.friendship.user1

        # Create a unique room name
        self.room_name = f'private_chat_{self.friendship_id}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    @database_sync_to_async
    def get_friendship_if_part_of(self):
        try:
            friendship = Friend.objects.select_related('user1', 'user2').get(id=self.friendship_id)
            if friendship.user1 == self.user or friendship.user2 == self.user:
                return friendship
            else:
                return None
        except Friend.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']

        # Save the message to the database
        message = await self.save_message(self.user, self.friend, message_content)

        # Send the message to the room group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_username': self.user.username,
                'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M'),
            }
        )

    async def chat_message(self, event):
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def save_message(self, sender, receiver, content):
        return Message.objects.create(sender=sender, receiver=receiver, content=content)
