from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import User


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return render(request, 'user/login.html')

        if check_password(password, user.password):
            request.session['user_id'] = user.id
            messages.success(request, "Login successful!")
            return redirect('profile')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'user/login.html')

def logout(request):
    user_id = request.session.get('user_id')
    if user_id:
        del request.session['user_id']
        messages.success(request, "You have been logged out.")
    return redirect('login')


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
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, "You need to log in to access the profile page.")
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    
    return render(request, 'user/profile.html', {'user': user})
