from rest_framework import serializers
from srcs.api.models import Match, Matchs, Tournament
from srcs.api.serializers.user import UserSerializer


class MatchSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)

    class Meta:
        model = Match
        fields = '__all__'


class MatchsSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    user3 = UserSerializer(read_only=True)
    user4 = UserSerializer(read_only=True)

    class Meta:
        model = Matchs
        fields = '__all__'


class TournamentSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    user3 = UserSerializer(read_only=True)
    user4 = UserSerializer(read_only=True)

    class Meta:
        model = Tournament
        fields = '__all__'
