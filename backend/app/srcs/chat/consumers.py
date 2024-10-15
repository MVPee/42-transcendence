from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth import get_user_model
import redis.asyncio as redis

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'global_chat'

        # Initialize Redis connection
        self.redis = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

        # Join the chat group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send previous messages to the user upon connection
        messages = await self.redis.lrange('chat_messages', 0, -1)
        for message in messages:
            message_data = json.loads(message)
            await self.send(text_data=json.dumps(message_data))

    async def disconnect(self, close_code):
        # Close the Redis connection
        await self.redis.close()

        # Leave the chat group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        user = self.scope['user']
        username = user.username if user.is_authenticated else 'Anonymous'

        message = {
            'message': message_content,
            'username': username
        }

        # Store the message in Redis
        await self.redis.rpush('chat_messages', json.dumps(message))
        await self.redis.ltrim('chat_messages', -100, -1)  # Keep only the last 100 messages

        # Send the message to the chat group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'username': username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send the message to the WebSocket client
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
