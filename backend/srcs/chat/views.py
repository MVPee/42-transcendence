from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from srcs.user.models import CustomUser as User
from django.db.models import Q
from django.contrib import messages
from .models import Friend, Blocked, Message

