from rest_framework.decorators import api_view, permission_classes
from srcs.api.permissions import APIKey
from srcs.game.models import Match, Matchs, Tournament
from srcs.user.models import CustomUser as User
from rest_framework.response import Response
from rest_framework import status
import os
    

@api_view(['POST'])
@permission_classes([APIKey])
def create_1v1_game(request):
    """
        api/game/1v1/add/
    """
    title = request.data.get('title')
    user1_username = request.data.get('user1_username')
    user2_username = request.data.get('user2_username')

    user1_instance = User.objects.filter(username=user1_username).first()
    user2_instance = User.objects.filter(username=user2_username).first()

    match = Match.objects.create(game=title, user1=user1_instance, user2=user2_instance)
    print(match)
    if match is not None:
        return Response({"id": match.id}, status=200)
    return Response(status=400)


@api_view(['POST'])
@permission_classes([APIKey])
def create_2v2_game(request):
    """
        api/game/2v2/add/
    """
    title = request.data.get('title')
    user1_username = request.data.get('user1_username')
    user2_username = request.data.get('user2_username')
    user3_username = request.data.get('user3_username')
    user4_username = request.data.get('user4_username')

    user1_instance = User.objects.filter(username=user1_username).first()
    user2_instance = User.objects.filter(username=user2_username).first()
    user3_instance = User.objects.filter(username=user3_username).first()
    user4_instance = User.objects.filter(username=user4_username).first()

    if title == 'tournament':
        match = Tournament.objects.create(user1=user1_instance, user2=user2_instance, user3=user3_instance, user4=user4_instance)
    else:
        match = Matchs.objects.create(game=title, user1=user1_instance, user2=user2_instance, user3=user3_instance, user4=user4_instance)
    if match is not None:
        return Response({"id": match.id}, status=200)
    return Response(status=400)