from django.contrib import admin
from .models import Message
from .models import Friend
from .models import Blocked

# Register your models here.
admin.site.register(Message)
admin.site.register(Friend)
admin.site.register(Blocked)