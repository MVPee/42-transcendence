from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Friend
from django.db.models import Q
from asgiref.sync import sync_to_async
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.id = self.scope['url_route']['kwargs']['id']
        self.room_group_name = f'chat_{self.id}'
        self.user = self.scope['user']

        print(self.id)
        
        is_valid = await self.validate_friendship()
        if not is_valid:
            await self.close()
            return

        await self.accept()
        await self.send(text_data=json.dumps({"message": "WebSocket connection established"}))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({"message": "Received: " + text_data}))

    @sync_to_async
    def validate_friendship(self):
        """
        Validates whether the connected user is a friend in the chat.
        Returns True if valid, False otherwise.
        """
        if not self.user.is_authenticated:
            return False

        # Assuming 'id' corresponds to a Friend relationship
        try:
            friend = Friend.objects.filter(
                (Q(user1=self.user.id) | Q(user2=self.user.id)),
                id=self.id,
                status=True
            ).first()
            return friend is not None
        except Friend.DoesNotExist:
            return False