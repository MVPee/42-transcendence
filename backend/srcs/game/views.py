from django.shortcuts import render

# Create your views here.
def index_view(request):
    return render(request, 'game/index.html')

def offline_view(request):
    return render(request, 'game/offline.html', {'script': 'js/offline_pong.js'})

def ai_view(request):
    return render(request, 'game/offline.html', {'script': 'js/ai_pong.js'})