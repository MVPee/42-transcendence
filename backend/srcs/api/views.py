from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def is_authenticated(request):
    """
    A api function who check if the user is authenticated or not.

    Returns:
        JsonResponse: is authentificated (true/false)
    """
    is_authenticated = request.user.is_authenticated
    return Response({'is_authenticated': is_authenticated}, status=status.HTTP_200_OK)
