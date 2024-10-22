from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from srcs.chat.models import Friend, Blocked
from django.db.models import Q 
from srcs.game.models import Match
from .models import CustomUser as User

def home_view(request):
    return render(request, 'base.html')