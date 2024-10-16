from django.contrib import admin
from .models import Tournament
from .models import TournamentMatch

# Register your models here.
admin.site.register(Tournament)
admin.site.register(TournamentMatch)