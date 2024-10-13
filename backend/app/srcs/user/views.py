from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import User

# Create your views here.
def login(request):
    # if request.method == "POST":
    return render(request, 'user/login.html')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if len(password) < 8:
            messages.error(request, "Password is not strong enought")
        elif len(password) > 32:
            messages.error(request, "Password is too big")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already used.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already used.")
        else:
            user = User(username=username, email=email, password=make_password(password))
            user.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
    return render(request, 'user/register.html')


def profile(request):
    return render(request, 'user/profile.html')