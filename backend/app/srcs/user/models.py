from django.utils import timezone
from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256, null=True)
    last_login = models.DateTimeField(null=True, blank=True)
    elo = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    defeat = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} . . . . {self.email} . . . . {self.created_at}"