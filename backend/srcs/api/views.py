from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def is_authenticated(request):
    """
    A api function who check if the user is authenticated or not.

    Returns:
        JsonResponse: is authentificated (true/false)
    """
    is_authenticated = request.user.is_authenticated
    return JsonResponse({'is_authenticated': is_authenticated})
