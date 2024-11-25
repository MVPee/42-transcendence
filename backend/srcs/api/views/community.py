from rest_framework.decorators import api_view, permission_classes
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
