from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os

API_KEY = os.getenv('API_KEY', '')

@api_view(['GET'])
def check_api_key(request):
    """
    This api is an exemple function for how can we create private api via api key in .env
    curl -k -X GET "https://42.mvpee.be/api/check_api_key/" -H "X-Api-Key: $API_KEY"
    
    A api function who check if the request has the correct api key in the header

    Returns:
        Response: has_apiKey (true/false)
    """
    api_key = request.headers.get('X-Api-Key')

    if api_key == API_KEY:
        return Response({'has_api_key': True}, status=status.HTTP_200_OK)
    return Response({'has_api_key': False}, status=status.HTTP_401_UNAUTHORIZED)