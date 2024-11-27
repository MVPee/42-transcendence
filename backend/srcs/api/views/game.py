from rest_framework.decorators import api_view, permission_classes
from srcs.api.permissions import APIKey
from srcs.game.models import Match, Matchs, Tournament
from srcs.user.models import CustomUser as User
from rest_framework.response import Response
from rest_framework import status
from srcs.api.serializers.match import MatchSerializer, MatchsSerializer, TournamentSerializer
import os
    

@api_view(['GET'])
def all_1v1_game(request):
    """
    Retrieve details of all 1v1 game match
    Endpoint: api/game/1v1/
    """
    try:
        matchs = Match.objects.all()
    except Match.DoesNotExist:
        return Response({"error": "No match found"}, status=404)
    
    serializer = MatchSerializer(matchs, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def all_2v2_game(request):
    """
    Retrieve details of all 2v2 game match
    Endpoint: api/game/2v2/
    """
    try:
        match = Matchs.objects.all()
    except Matchs.DoesNotExist:
        return Response({"error": "no 2v2 match found"}, status=404)
    
    serializer = MatchsSerializer(match, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def all_tournament_game(request):
    """
    Retrieve details of all tournament match
    Endpoint: api/game/tournament/
    """
    try:
        match = Tournament.objects.all()
    except Tournament.DoesNotExist:
        return Response({"error": "No tournament found"}, status=404)
    
    serializer = TournamentSerializer(match, many=True)
    return Response(serializer.data, status=200)




@api_view(['GET'])
def get_1v1_game(request, id):
    """
    Retrieve details of a specific game match.
    Endpoint: api/game/1v1/<int:id>/
    """
    try:
        match = Match.objects.get(id=id)
    except Match.DoesNotExist:
        return Response({"error": "Match 1v1 not found"}, status=404)
    
    serializer = MatchSerializer(match)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def get_2v2_game(request, id):
    """
    Retrieve details of a specific game match.
    Endpoint: api/game/2v2/<int:id>/
    """
    try:
        match = Matchs.objects.get(id=id)
    except Matchs.DoesNotExist:
        return Response({"error": "Match 2v2 not found"}, status=404)
    
    serializer = MatchsSerializer(match)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def get_tournament_game(request, id):
    """
    Retrieve details of a specific game match.
    Endpoint: api/game/tournament/<int:id>/
    """
    try:
        match = Tournament.objects.get(id=id)
    except Tournament.DoesNotExist:
        return Response({"error": "Tournament not found"}, status=404)
    
    serializer = TournamentSerializer(match)
    return Response(serializer.data, status=200)




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




@api_view(['POST'])
@permission_classes([APIKey])
def game_1v1_set_score(request):
    """
        api/game/1v1/score/set/
        {
            "id": 2, #? GAME_ID
            "player_id": 1, #?PLAYER_ID
            "score": 1231 #?SCORE FOR THE PLAYER
        }
    """
    game_id = request.data.get('id')
    player_id = request.data.get('player_id')
    score = request.data.get('score')

    game = Match.objects.filter(id=game_id).first()
    if game is None:
        return Response({"error": "Game not found."}, status=400)

    if game.user1.id == player_id:
        game.user1_score = score
    elif game.user2.id == player_id:
        game.user2_score = score
    else:
        return Response({"error": "User not found."}, status=400)
    game.save()

    serialize = MatchSerializer(game)
    return Response(serialize.data ,status=200)


@api_view(['POST'])
@permission_classes([APIKey])
def game_2v2_set_score(request):
    """
        api/game/2v2/score/set/
        {
            "id": 2, #? GAME_ID
            "team": 1, #?PLAYER_ID
            "score": 1231 #?SCORE FOR THE TEAM
        }
    """
    game_id = request.data.get('id')
    team = request.data.get('team')
    score = request.data.get('score')

    game = Matchs.objects.filter(id=game_id).first()
    if game is None:
        return Response({"error": "Game not found."}, status=400)

    if team == 1:
        game.team1_score = score
    elif team == 2:
        game.team2_score = score
    else:
        return Response({"error": "User not found."}, status=400)
    game.save()

    serialize = MatchsSerializer(game)
    return Response(serialize.data ,status=200)


@api_view(['POST'])
@permission_classes([APIKey])
def update_tournament(request):
    """
        api/tournament/update/
        {
            "tournament_id": 17,
            "player1_position": 4,
            "player2_position": 2,
            "player3_position": 1,
            "player4_position": 3,
            "winner_id": 1
        }
    """
    tournament_id = request.data.get('tournament_id')
    player1_position = request.data.get('player1_position')
    player2_position = request.data.get('player2_position')
    player3_position = request.data.get('player3_position')
    player4_position = request.data.get('player4_position')
    winner_id = request.data.get('winner_id')

    winner_instance = User.objects.filter(id=winner_id).first()
    if winner_instance is None:
        return Response({"error": "Winner not found."}, status=400)
    tournament = Tournament.objects.filter(id=tournament_id).first()
    if tournament is None:
        return Response({"error": "Tournament not found."}, status=400)

    tournament.user1_position = player1_position
    tournament.user2_position = player2_position
    tournament.user3_position = player3_position
    tournament.user4_position = player4_position
    tournament.winner = winner_instance
    tournament.save()

    serialize = TournamentSerializer(tournament)
    return Response(serialize.data , status=200)
