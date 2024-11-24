from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout as auth_logout

@api_view(['GET'])
def is_authenticated(request):
    """
    A api function who check if the user is authenticated or not.

    Returns:
        Response: is authentificated (true/false)
    """
    is_authenticated = request.user.is_authenticated
    return Response({'is_authenticated': is_authenticated}, status=status.HTTP_200_OK)

@api_view(['POST'])
def logout(request):
    """
    A api function who logout the user if the user is authenticated

    Returns:
        Response: is authentificated (true/false)
    """
    if request.user.is_authenticated:
        auth_logout(request)
        return Response({'logout': True}, status=status.HTTP_200_OK)
    return Response({"logout": True}, status=400)
