from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    elo = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    defeat = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} . . . . {self.email} . . . . {self.created_at}"