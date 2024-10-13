from django.contrib import admin
from .models import Tournaments
from .models import Tournament_match

# Register your models here.
admin.site.register(Tournaments)
admin.site.register(Tournament_match)