from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout as auth_logout, authenticate, login as auth_login
from srcs.user.models import CustomUser as User
import os

API_KEY = os.getenv('API_KEY', '')

@api_view(['GET'])
def check_api_key(request):
    """
    This api is an exemple function for how can we create private api via api key in .env
    curl -k -X GET "https://42.mvpee.be/api/check_api_key/" -H "X-Api-Key: $API_KEY"
    
    A api function who check if the request has the correct api key in the header

    Returns:
        Response: has_apiKey (true/false)
    """
    api_key = request.headers.get('X-Api-Key')

    if api_key == API_KEY:
        return Response({'has_api_key': True}, status=status.HTTP_200_OK)
    return Response({'has_api_key': False}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def is_authenticated(request):
    """
    A api function who check if the user is authenticated or not.

    Returns:
        Response: is authentificated (true/false)
    """
    is_authenticated = request.user.is_authenticated
    return Response({'is_authenticated': is_authenticated}, status=status.HTTP_200_OK)

@api_view(['POST'])
def logout(request):
    """
    A api function who logout the user if the user is authenticated

    Returns:
        Response: logout (true/false), message (error, success)
    """
    if request.user.is_authenticated:
        auth_logout(request)
        return Response({'logout': True, "success_message": "Logout successfull."}, status=status.HTTP_200_OK)
    return Response({"logout": True, "error_message": "Already logout."}, status=400)

@api_view(['POST'])
def login(request):
    """
    A api function who login the user if the user is not authenticated

    Returns:
        Response: login (true/false), message (error, success)
    """
    if request.user.is_authenticated:
        return Response({
            'login': False,
            'error_message': 'You are already logged in. Please logout first.'
        }, status=status.HTTP_400_BAD_REQUEST)

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({
            'login': False,
            'error_message': 'Username and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        auth_login(request, user)
        return Response({
            'login': True,
            'success_message': 'Login successful.'
        }, status=status.HTTP_200_OK)

    return Response({
        'login': False,
        'error_message': 'Invalid username or password.'
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def register(request):
    """
    API function to register a new user and log them in if successful.
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    if len(username) < 5 or len(username) > 20:
        return Response({
            'register': False,
            'error_message': 'Username is too short (< 5) or too long (> 20).'
        }, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 5 or len(password) > 32:
        return Response({
            'register': False,
            'error_message': 'Password is too short (< 5) or too long (> 32).'
        }, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({
            'register': False,
            'error_message': 'Username already exists.'
        }, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({
            'register': False,
            'error_message': 'Email already in use.'
        }, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({
            'register': False,
            'error_message': 'Passwords do not match.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        auth_login(request, user)
        return Response({
            'register': True,
            'success_message': 'Registration successful. You are now logged in.'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'register': False,
            'error_message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
