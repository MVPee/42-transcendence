from django.shortcuts import render
from srcs.user.models import CustomUser as User

# Create your views here.
def index_view(request):
    users = User.objects.all().order_by('-elo')
    return render(request, 'game/index.html', {'users': users})

def offline_view(request):
    return render(request, 'game/offline.html', {'script': 'js/offline_pong.js'})

def ai_view(request):
    return render(request, 'game/offline.html', {'script': 'js/ai_pong.js'})