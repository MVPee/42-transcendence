from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    print(request.user.is_authenticated)
    return render(request, 'tournaments/index.html')