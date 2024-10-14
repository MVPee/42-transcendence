from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.
def index_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access the profile page.")
        return redirect('login')
    return render(request, 'chat/index.html')