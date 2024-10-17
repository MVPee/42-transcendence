from django.utils import timezone
from django.db import models
from srcs.game.models import Match
from django.conf import settings

class Tournament(models.Model):
    name = models.CharField(max_length=25)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        winner_name = self.winner.username if self.winner else "No winner yet"
        return f"{self.name} won by {winner_name}, {self.created_at}"

class TournamentMatch(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    round = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.tournament.name}, {self.match}, Round {self.round}"
