from django.db import models
from django.conf import settings
from django.utils import timezone

class Friend(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships_initiated')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships_received')
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        if (self.status):
            return f"{self.user1.username} <3 {self.user2.username}"
        return f"{self.user1.username} send a request friends to {self.user2.username}"


class Blocked(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocks_initiated')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocks_received')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1.username} blocked {self.user2.username}"
    

class Messages(models.Model):
    friend_id = models.ForeignKey(Friend, on_delete=models.CASCADE, related_name='friend_chat_id')
    sender_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_sender')
    context = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if (self.sender_id.id == self.friend_id.user1 ):
            receiver = self.friend_id.user2
        else: receiver = self.friend_id.user1
        return f"{self.sender_id.username} sent {self.context} to {receiver.username}"