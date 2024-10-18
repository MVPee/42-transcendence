from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from srcs.chat.models import Friend, Blocked
from django.db.models import Q 
from srcs.game.models import Match
from .models import CustomUser as User

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

@login_required
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

@login_required
def profile_view(request):
    games = Match.objects.filter(
        Q(user1=request.user) |
        Q(user2=request.user)
    )
    return render(request, 'user/profile.html', {
        'user': request.user,
        'games': games
    })

@login_required
def private_profile_view(request, username):
    userProfile = get_object_or_404(User, username=username)
    
    # Check if the users are friends
    friendship = Friend.objects.filter(
        Q(user1=request.user, user2=userProfile) | 
        Q(user2=request.user, user1=userProfile),
        status=True
    ).first()

    # or pending
    pending_friendship = Friend.objects.filter(
        Q(user1=request.user, user2=userProfile) | 
        Q(user2=request.user, user1=userProfile),
        status=False
    ).first()

    #Check if the users is blocked
    blockship = Blocked.objects.filter(
        Q(user1=request.user, user2=userProfile) | 
        Q(user2=request.user, user1=userProfile),
    ).first()

    games = Match.objects.filter(
        Q(user1=userProfile) |
        Q(user2=userProfile)
    )

    # Pass the friendship status to the template
    return render(request, 'user/profile.html', {
        'user': userProfile,
        'friendship': friendship,
        'pending_friendship': pending_friendship,
        'blockship': blockship,
        'games': games
    })