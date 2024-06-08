from django.contrib import auth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import (
    require_GET, require_http_methods, require_POST,
)

from app.forms import LoginForm, RegisterForm


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@require_POST
def login(request):
    login_form = LoginForm(data=request.POST)
    if login_form.is_valid():
        user = auth.authenticate(request, **login_form.cleaned_data)

        if user:
            auth.login(request, user)
            return JsonResponse({'status': 'ok'}, status=200)
        return JsonResponse({'error': 'Wrong username or password'}, status=400)
    return JsonResponse({'error': 'Bad Request'}, status=400)


@require_POST
def register(request):
    user_form = RegisterForm(data=request.POST)
    if user_form.is_valid():
        user = user_form.save()

        if user:
            auth.login(request, user)
            return JsonResponse({'status': 'ok'}, status=400)
        else:
            return JsonResponse({'error': 'User saving error'}, status=400)

    return JsonResponse(user_form.errors, status=400)


@require_POST
def logout(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated'}, status=400)

    try:
        auth.logout(request)
        return JsonResponse({'status': 'ok'}, status=200)
    except Exception as e:
        return JsonResponse({'error': 'Internal error'}, status=500)
