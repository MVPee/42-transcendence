from rest_framework import serializers
from srcs.user.models import CustomUser as User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'elo', 'created_at']