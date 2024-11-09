from django.utils import timezone
from django.db import models
from django.conf import settings

class Match(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='first_opponents', null=True)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='second_opponents', null=True)
    user1_score = models.IntegerField(default=0)
    user2_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user1.username if self.user1 else 'deleted user'} vs {self.user2.username if self.user2 else 'deleted user'}: {self.user1_score}/{self.user2_score}"