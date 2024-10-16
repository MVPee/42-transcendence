from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index_view(request):
    return render(request, 'chat/index.html')

@login_required
def global_chat_view(request):
    return render(request, 'chat/global.html')