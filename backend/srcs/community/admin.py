from django.contrib import admin
from .models import *

admin.site.register(Friend)
admin.site.register(Blocked)
admin.site.register(Messages)