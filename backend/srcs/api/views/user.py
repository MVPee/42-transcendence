from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from srcs.api.permissions import APIKey
from rest_framework import status
from django.core.files.images import get_image_dimensions
from django.contrib.auth import logout as auth_logout, authenticate, login as auth_login
from srcs.user.models import CustomUser as User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from srcs.community.models import Friend, Blocked
from django.db.models import Q
from srcs.api.serializers.settings import SettingsSerializer
from srcs.api.serializers.user import UserSerializer
import os

API_KEY = os.getenv('API_KEY', '')


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
    return Response({"logout": True, "error_message": "Already logout."}, status=status.HTTP_400_BAD_REQUEST)


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
    
    if username == 'AI.':
        return Response({
            'login': False,
            'error_message': 'Are you a robot?'
        }, status=status.HTTP_401_UNAUTHORIZED)

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

    if username == "System":
        return Response({
            'register': False,
            'error_message': 'Are you a hacker??'
        }, status=status.HTTP_401_UNAUTHORIZED)

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
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def settings(request):
    serializer = SettingsSerializer(data=request.data)

    if serializer.is_valid():
        action = serializer.validated_data['action']
        value = serializer.validated_data.get('value')
        avatar = serializer.validated_data.get('avatar')
        user = request.user

        # Handle avatar update
        if action == 'avatar' and avatar:

            # Delete old avatar
            if user.avatar.name != 'avatars/profile.png':
                old_avatar_path = os.path.join('/frontend/media', user.avatar.name)
                if os.path.isfile(old_avatar_path):
                    os.remove(old_avatar_path)

            user.avatar = avatar
            user.save()
            return Response({'success_message': 'Avatar updated successfully.'})

        # Handle username update
        elif action == 'username' and value:

            if value == 'AI.' or value == 'System':
                return Response({'error_message': 'No robots allowed...'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=value).exclude(id=user.id).exists():
                return Response({'error_message': 'Username already taken.'}, status=status.HTTP_400_BAD_REQUEST)
            elif user.username == value:
                return Response({'error_message': 'You need to use your keyboard to change your username.'}, status=status.HTTP_400_BAD_REQUEST)
            elif len(value) < 5 or len(value) > 20:
                return Response({'error_message': 'Your username need to be between 5 and 20 characters.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.username = value
                user.save()
                return Response({'success_message': f'Username updated successfully to {value}'})

        # Handle email update
        elif action == 'email' and value:
            if User.objects.filter(email=value).exclude(id=user.id).exists():
                return Response({'error_message': 'Email already taken.'}, status=status.HTTP_400_BAD_REQUEST)
            elif user.email == value:
                return Response({'error_message': 'You need to use your keyboard to change your email.'}, status=status.HTTP_400_BAD_REQUEST)
            elif len(value) < 6 or len(value) > 32:
                return Response({'error_message': 'Your email need to be between 6 and 32 characters.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.email = value
                user.save()
                return Response({'success_message': f'Email updated successfully to {value}'})

        # Handle language update
        elif action == 'language' and value:
            if user.language == value:
                return Response({'error_message': 'You need to use your mouse to change your language.'}, status=status.HTTP_400_BAD_REQUEST)
            elif value in ['EN', 'FR', 'DE']:
                user.language = value
                user.save()
                return Response({'success_message': 'Language updated successfully.'})
            else:
                return Response({'error_message': 'Invalid language selection.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'error_message': 'Invalid action or missing value.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        error_messages = [f"{', '.join(errors)}" for field, errors in serializer.errors.items()]
        return Response({'error_message': error_messages}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_by_id(request, id):
    user = User.objects.filter(id=id).first()
    if user is None:
        return Response({"error": "No user with this ID."}, status=404)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def get_user_by_username(request, username):
    user = User.objects.filter(username=username).first()
    if user is None:
        return Response({"error": "No user with this username."}, status=404)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=200)


@api_view(['GET'])
@permission_classes([APIKey])
def add_elo(request, id, nbr):
    """
        /api/users/<int:id>/elo/add/<int:nbr>
    """
    user_instance = User.objects.filter(id=id).first()
    if user_instance is None:
        return Response({"error": "User not found"}, status=400)

    user_instance.elo += nbr
    user_instance.save()

    serializer = UserSerializer(user_instance)
    return Response(serializer.data, status=200)


@api_view(['GET'])
@permission_classes([APIKey])
def remove_elo(request, id, nbr):
    """
        /api/users/<int:id>/elo/remove/<int:nbr>
    """
    user_instance = User.objects.filter(id=id).first()
    if user_instance is None:
        return Response({"error": "User not found"}, status=400)

    user_instance.elo -= nbr
    if user_instance.elo < 0: user_instance.elo = 0
    user_instance.save()

    serializer = UserSerializer(user_instance)
    return Response(serializer.data, status=200)
