from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser

def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'user/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
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
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already used.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already used.")
        else:
            user = CustomUser(username=username, email=email, password=make_password(password))
            user.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
    return render(request, 'user/register.html')

@login_required
def profile_view(request):
    return render(request, 'user/profile.html', {'user': request.user})
