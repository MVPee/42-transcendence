from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request, 'user/login.html')

def register(request):
    return render(request, 'user/register.html')

def profile(request):
    return render(request, 'user/profile.html')