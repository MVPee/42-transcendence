from rest_framework import serializers
from django.core.files.images import get_image_dimensions
from django.core.validators import EmailValidator

class SettingsSerializer(serializers.Serializer):
    action = serializers.CharField(required=True)
    value = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False)

    def validate_action(self, value):
        valid_actions = ['avatar', 'username', 'email', 'language']
        if value not in valid_actions:
            raise serializers.ValidationError('Invalid action.')
        return value

    def validate_avatar(self, value):
        if value:
            valid_extensions = ['png', 'jpeg', 'jpg']
            if value.name.split('.')[-1].lower() not in valid_extensions:
                raise serializers.ValidationError('Invalid file format. Only PNG, JPEG, and JPG are allowed.')

            if value.size > 1 * 1024 * 1024:  # Max file size 1 MB
                raise serializers.ValidationError('File size too large. Max size is 1MB.')

            width, height = get_image_dimensions(value)
            if width < 50 or height < 50 or width > 256 or height > 256:
                raise serializers.ValidationError('Avatar dimensions should be between 50x50 pixels and 256x256 pixels.')

            return value
        return value

    def validate_value(self, value):
        action = self.initial_data.get('action', None)
        if action == 'email':
            email_validator = EmailValidator()
            try:
                email_validator(value)
            except Exception as e:
                raise serializers.ValidationError("Only valid email allowed.")
        return value
