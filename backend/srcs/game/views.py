from django.shortcuts import render
from srcs.user.models import CustomUser as User
from django.contrib.auth.decorators import login_required


@login_required
def index_view(request):
    users = User.objects.all().order_by('-elo')
    return render(request, 'game/index.html', {'users': users})

@login_required
def offline_view(request):
    return render(request, 'game/offline.html', {'script': 'js/offline_pong.js'})

@login_required
def ai_view(request):
    return render(request, 'game/offline.html', {'script': 'js/ai_pong.js'})