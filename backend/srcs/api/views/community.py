from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from srcs.user.models import CustomUser as User
from srcs.community.models import Friend, Blocked, Messages
from django.shortcuts import get_object_or_404
from django.db.models import Q
from srcs.api.permissions import APIKey
import os

API_KEY = os.getenv('API_KEY', '')


@api_view(['GET'])
def get_friendship(request, pk):
    """
        api/friendship/<int:pk>/
    """
    friendship = get_object_or_404(Friend, id=pk)
    data = {
        "id": friendship.id,
        "user1": friendship.user1.id,
        "user2": friendship.user2.id,
        "status": friendship.status
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def check_friendship(request, user1, user2):
    """
        api/check_friendship/<int:user1>/<int:user2>/
    """
    user1_instance = get_object_or_404(User, id=user1)
    user2_instance = get_object_or_404(User, id=user2)

    try:
        friendship = Friend.objects.get(
            (Q(user1=user1_instance) & Q(user2=user2_instance)) | 
            (Q(user1=user2_instance) & Q(user2=user1_instance)),
            status=True
        )
        
        return Response({ 'success': True }, status=status.HTTP_200_OK)
    
    except Friend.DoesNotExist:
        return Response({ 'success': False }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([APIKey])
def add_message(request):
    """
        api/message/add/
    """
    api_key = request.data.get('X-Api-Key')
    if api_key != API_KEY:
        return Response({'success': False, 'error': 'Bad API_KEY.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        friendship_id = request.data.get('friendship')
        sender_id = request.data.get('sender')
        message = request.data.get('message')

        if not friendship_id or not sender_id or not message:
            return Response(
                {"success": False, "error": "Missing required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        friend_instance = get_object_or_404(Friend, id=friendship_id)
        sender_instance = get_object_or_404(User, id=sender_id)

        message = Messages.objects.create(
            friend_id=friend_instance,
            sender_id=sender_instance,
            context=message
        )

        return Response(
            {"success": True, "message_id": message.id},
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        print(f"Error: {str(e)}") #* DEBUG
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def friend(request):
    profile = request.data.get('profile')
    action = request.data.get('type')

    if not profile or not action:
        return Response({'error_message': 'Profile and type are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user_instance = User.objects.filter(username=profile).first()
    if not user_instance:
        return Response({'error_message': f'User {profile} does not exist. Maybee reload the profile page.'}, status=status.HTTP_404_NOT_FOUND)

    if user_instance == request.user:
        return Response({'error_message': 'You cannot perform this action on yourself.'}, status=status.HTTP_400_BAD_REQUEST)

    friend = Friend.objects.filter(Q(user1=request.user, user2=user_instance) | Q(user1=user_instance, user2=request.user)).first()
    block = Blocked.objects.filter(Q(user1=request.user, user2=user_instance) | Q(user1=user_instance, user2=request.user)).first()

    if action == 'add':
        if block:
            return Response({'error_message': f"You cannot send a friend request to {profile} due to a block."}, status=status.HTTP_403_FORBIDDEN)

        if friend:
            if friend.status:
                return Response({'error_message': f'You are already friends with {profile}.'}, status=status.HTTP_400_BAD_REQUEST)
            elif friend.user1 == request.user:
                return Response({'error_message': f'A friend request was already sent to {profile}.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                friend.status = True
                friend.save()
                return Response({"profile": profile, 'success_message': f'You and {profile} are now friends!'}, status=status.HTTP_200_OK)
        else:
            Friend.objects.create(user1=request.user, user2=user_instance, status=False)
            return Response({"profile": profile, 'success_message': f'Friend request sent to {profile}.'}, status=status.HTTP_200_OK)

    elif action == 'remove':
        if not friend:
            return Response({'error_message': f"{profile} is not in your friend list."}, status=status.HTTP_400_BAD_REQUEST)

        if friend.status:
            friend.delete()
            return Response({"profile": profile, 'success_message': f"{profile} has been removed from your friends."}, status=status.HTTP_200_OK)
        elif friend.user1 == request.user:
            friend.delete()
            return Response({"profile": profile, 'success_message': f"{profile}'s friend request successfully canceled."}, status=status.HTTP_200_OK)
        else:
            return Response({'error_message': f"No pending friend request to {profile}."}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'error_message': 'Invalid action. Must be "add" or "remove".'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block(request):
    profile = request.data.get('profile')
    type = request.data.get('type')

    if not profile or not type:
        return Response({'error_message': 'Profile and type are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user_instance = User.objects.filter(username=profile).first()
    if not user_instance:
        return Response({'error_message': f'User {profile} does not exist. Maybee reload the profile page.'}, status=status.HTTP_404_NOT_FOUND)

    if user_instance == request.user:
        return Response({'error_message': 'You cannot block yourself.'}, status=status.HTTP_400_BAD_REQUEST)

    if type == 'add':
        existing_block = Blocked.objects.filter(user1=request.user, user2=user_instance).first()
        if existing_block:
            return Response({'error_message': f'{profile} is already blocked.'}, status=status.HTTP_400_BAD_REQUEST)

        Blocked.objects.create(user1=request.user, user2=user_instance)

        Friend.objects.filter(Q(user1=request.user, user2=user_instance) | Q(user1=user_instance, user2=request.user)).delete()

        return Response({"profile": profile, 'success_message': f'Successfully blocked {profile}.'}, status=status.HTTP_200_OK)

    elif type == 'remove':
        existing_block = Blocked.objects.filter(user1=request.user, user2=user_instance).first()
        if not existing_block:
            return Response({'error_message': f'{profile} is not blocked.'}, status=status.HTTP_400_BAD_REQUEST)
        existing_block.delete()
        return Response({"profile": profile, 'success_message': f'{profile} is no longer blocked.'}, status=status.HTTP_200_OK)

    else:
        return Response({'error_message': 'Invalid type. Must be "add" or "remove".'}, status=status.HTTP_400_BAD_REQUEST)
