from django.utils import timezone
from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=50)
    mail = models.EmailField()
    password = models.CharField(max_length=128, null=True)
    elo = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    defeat = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} . . . . {self.mail} . . . . {self.created_at}"