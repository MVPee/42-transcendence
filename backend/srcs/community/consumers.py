from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Friend, Messages
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

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        await self.channel_layer.group_send(self.room_group_name,{
            'type': 'chatroom_message',
            'username': username,
            'message': message,
        })
        await self.add_chatdb(message)


    @sync_to_async
    def validate_friendship(self):
        """
        Validates whether the connected user is a friend in the chat.
        Returns True if valid, False otherwise.
        """
        if not self.user.is_authenticated:
            return False

        return self.get_friendship() != None
        
    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'username': username,
            'message': message,
        }))

    @sync_to_async
    def add_chatdb(self, message):
        friendship = self.get_friendship()
        new_message = Messages.objects.create(friend_id=friendship, sender_id=self.user, context=message)
        new_message.save()

    def get_friendship(self):
        # Assuming 'id' corresponds to a Friend relationship
        try:
            friend = Friend.objects.filter(
                (Q(user1=self.user.id) | Q(user2=self.user.id)),
                id=self.id,
                status=True
            ).first()
            return friend
        except Friend.DoesNotExist:
            return None