from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', default='avatars/profile.png', blank=True)
    elo = models.IntegerField(default=0)
    language = models.CharField(default="EN")
    last_connection = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} . . . . {self.email} . . . . {self.created_at}"