from rest_framework import serializers
from srcs.api.models import CustomUser as User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'elo', 'avatar', 'created_at']