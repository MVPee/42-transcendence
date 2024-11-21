from django.utils import timezone
from django.db import models
from django.conf import settings

class Match(models.Model):
    game = models.CharField(default="pong_1v1", max_length=50)
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='match_first_opponents', null=True)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='match_second_opponents', null=True)
    user1_score = models.IntegerField(default=0)
    user2_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user1.username if self.user1 else 'deleted user'} vs {self.user2.username if self.user2 else 'deleted user'}: {self.user1_score}/{self.user2_score}: {self.game}"

    class Meta:
        verbose_name = "Match 1v1"
        verbose_name_plural = "Matchs 1v1"
        ordering = ['-created_at']


class Matchs(models.Model):
    game = models.CharField(default="pong_2v2", max_length=50)
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='matchs_first_opponents_1', null=True)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='matchs_second_opponents_1', null=True)
    user3 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='matchs_first_opponents_2', null=True)
    user4 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='matchs_second_opponents_2', null=True)
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user1.username if self.user1 else 'deleted user'} && {self.user2.username if self.user2 else 'deleted user'} ({self.team1_score}) VS ({self.team2_score}) {self.user3.username if self.user3 else 'deleted user'} && {self.user4.username if self.user4 else 'deleted user'}"

    class Meta:
        verbose_name = "Match 2v2"
        verbose_name_plural = "Matchs 2v2"
        ordering = ['-created_at']

class Tournament(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='tournaments_first_opponents_1', null=True)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='tournaments_second_opponents_1', null=True)
    user3 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='tournaments_first_opponents_2', null=True)
    user4 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='tournaments_second_opponents_2', null=True)
    user1_position = models.IntegerField(default=4)
    user2_position = models.IntegerField(default=4)
    user3_position = models.IntegerField(default=4)
    user4_position = models.IntegerField(default=4)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='tournaments_winner', null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Winner of the tournament {self.winner.username if self.winner else 'deleted user or no winner yet'}"

    class Meta:
        verbose_name = "Tournament 1v1v1v1"
        verbose_name_plural = "Tournaments 1v1v1v1"
        ordering = ['-created_at']