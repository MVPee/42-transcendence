from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Friend)
admin.site.register(Blocked)
admin.site.register(Messages)
admin.site.register(Match)
admin.site.register(Matchs)
admin.site.register(Tournament)