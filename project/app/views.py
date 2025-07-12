from django.shortcuts import render

# from django.contrib.auth import get_user_model

# User = get_user_model()


def index(request):
    return render(request, 'index.html')