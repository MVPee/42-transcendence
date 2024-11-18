from channels.generic.websocket import AsyncWebsocketConsumer
from ..models import Friend, Messages
from django.db.models import Q
from asgiref.sync import sync_to_async
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.id = self.scope['url_route']['kwargs']['id']
        self.room_group_name = f'chat_{self.id}'
        self.user = self.scope['user']
        
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
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            username = self.user.username
            await self.channel_layer.group_send(self.room_group_name,{
                'type': 'chatroom_message',
                'username': username,
                'message': message,
            })
            await self.add_chatdb(message)
            await self.send_notification_to_friend(message)
        except json.JSONDecodeError:
            print(text_data)

    async def send_notification_to_friend(self, message):
        """
        Send a notification to the other user in the friendship.
        """
        friend_user = await self.get_friend_user()
        if friend_user:
            await self.channel_layer.group_send(
                f'notification_{friend_user.id}',  # Friend's private notification group
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
        friendship = self.get_friendship()
        if friendship:
            if friendship.user1.id == self.user.id:
                return friendship.user2
            return friendship.user1
        return None

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
        if len(message) <= 100:
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