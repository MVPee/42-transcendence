from django.shortcuts import render
from srcs.user.models import CustomUser

# Create your views here.
def index(request):
    return render(request, 'home/index.html')