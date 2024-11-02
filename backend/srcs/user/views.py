from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser as User
from django.http import JsonResponse


def base_view(request):
    return render(request, 'base.html')

from django.shortcuts import render
from django.http import JsonResponse

def get_html(request, page):
    pages_config = {
        'home': {'template': 'home.html', 'auth_required': False},
        'profile': {'template': 'profile.html', 'auth_required': True},
        'login': {'template': 'login.html', 'auth_required': False},
    }
    
    page_config = pages_config.get(page)
    
    if not page_config:
        return JsonResponse({'html': "<p>404: NOT FOUND</p>"})

    if page_config['auth_required'] and not request.user.is_authenticated:
        login_content = render(request, 'login.html').content.decode("utf-8")
        return JsonResponse({
            'html': login_content,
            'error': "You must be logged in to access this page."
        })
    
    # Render the requested page's content
    html_content = render(request, page_config['template']).content.decode("utf-8")
    return JsonResponse({'html': html_content})
