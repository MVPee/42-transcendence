from django.utils import timezone
from django.db import models
from srcs.user.models import User


class Message(models.Model):
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender')
    friend_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reciever')
    context = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sender_id.username} sent to {self.friend_id.username}: {self.context}"

class Friend(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_initiated')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_received')
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        if (self.status):
            return f"{self.user1.username} <3 {self.user2.username}"
        return f"{self.user1.username} send a request friends to {self.user2.username}"


class Blocked(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocks_initiated')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocks_received')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1.username} blocked {self.user2.username}"