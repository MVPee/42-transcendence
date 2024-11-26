from rest_framework.permissions import BasePermission
from django.conf import settings
import os

class APIKey(BasePermission):
    """
    Custom permission to check if a valid API key is provided.
    """
    def has_permission(self, request, view):
        api_key = request.headers.get('X-API-KEY') or request.COOKIES.get('X-API-KEY')
        return api_key == os.getenv('API_KEY', '')
