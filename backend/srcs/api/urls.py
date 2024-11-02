from django.urls import path
from . import views
from .views import APIView

urlpatterns = [
    path('view/<str:page>/', APIView.as_view(), name='get_view'),
]
