import json
import time  # Token generation

import jwt  # Token generation

from cent import Client, PublishRequest  # Centrifugo
from django.contrib import auth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.decorators.http import (
    require_GET, require_http_methods, require_POST,
)

from app.forms import LoginForm, RegisterForm
from app.models import Chat, ChatParticipant, Message, Profile
from msgr import settings


@require_GET
def get_centrifugo_token(request):
    user_id = request.user.profile.id
    ws_url = settings.CENTRIFUGO_WS_URL
    secret = settings.CENTRIFUGO_SECRET
    token = jwt.encode(
        {'sub': str(user_id), 'exp': int(time.time()) + 10 * 60}, secret, algorithm="HS256"
    )

    return JsonResponse({
        'token': token,
        'url': ws_url
    })


def index(request):
    return render(request, '/app/test.html')


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
    except Exception:
        return JsonResponse({'error': 'Internal error'}, status=500)


@require_POST
def send_message(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated'}, status=400)

    api_url = settings.CENTRIFUGO_API_URL
    api_key = settings.CENTRIFUGO_API_KEY

    try:
        body = json.loads(request.body)

        client = Client(api_url, api_key)  # TODO: Возможно не стоит каждый раз создавать клиент
        ws_channel_name = 'chat_' + str(body['chatId'])
        publist_request = PublishRequest(
            channel=ws_channel_name,
            data={
                'type': 'send_message',
                'data': {
                    'text': body['text'],
                    'senderId': request.user.id,
                }
            })
        client.publish(publist_request)

        # Save the message to the database
        msg = Message.objects.create(chat=Chat.objects.get(pk=int(body['chatId'])),
                                    profile=request.user.profile,
                                    text=body['text'])
        msg.save()
    except json.JSONDecodeError or KeyError:
        return JsonResponse({'error': 'Bad Request'}, status=400)

    return JsonResponse({'status': 'ok'}, status=200)


@require_http_methods(['PATCH'])
def edit_message(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated'}, status=400)

    api_url = settings.CENTRIFUGO_API_URL
    api_key = settings.CENTRIFUGO_API_KEY

    try:
        body = json.loads(request.body)

        client = Client(api_url, api_key)  # TODO: Возможно не стоит каждый раз создавать клиент
        ws_channel_name = 'chat_' + str(body['chatId'])
        request = PublishRequest(
            channel=ws_channel_name,
            data={
                'type': 'edit_message',
                'data': {
                    'messageId': body['messageId'],
                    'text': body['text'],
                }
            })
        client.publish(request)

        # Update the message
        Message.objects.filter(pk=int(body['messageId'])).update(text=body['text'])
    except json.JSONDecodeError or KeyError:
        return JsonResponse({'error': 'Bad Request'}, status=400)

    return JsonResponse({'status': 'ok'}, status=200)


@require_http_methods(['DELETE'])
def delete_message(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated'}, status=400)

    try:
        body = json.loads(request.body)

        # Delete the message from the database
        msg = Message.objects.filter(pk=int(body['messageId']))
        if not msg.exists():
            return JsonResponse({'error': 'Message does not exist'}, status=400)

        msg.delete()

        # Send a message to Centrifugo to delete the message from the chat
        api_url = settings.CENTRIFUGO_API_URL
        api_key = settings.CENTRIFUGO_API_KEY

        client = Client(api_url, api_key)  # TODO: Возможно не стоит каждый раз создавать клиент
        ws_channel_name = 'chat_' + str(body['chatId'])
        request = PublishRequest(
            channel=ws_channel_name,
            data={
                'type': 'delete_message',
                'data': {
                    'messageId': body['messageId']
                }
            })
        client.publish(request)
    except json.JSONDecodeError or KeyError:
        return JsonResponse({'error': 'Bad Request'}, status=400)

    return JsonResponse({'status': 'ok'}, status=200)


def get_profile_info(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    if not profile:
        return JsonResponse({'error': 'Profile does not exist'}, status=400)
    return JsonResponse({'username': profile.user.username,
                         'name': profile.name,
                         'bio': profile.bio,
                         'last_active': profile.last_active
                         }, status=200)


class SelfProfileView(View):
    model = Profile

    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User is not authenticated'}, status=400)

        profile = request.user.profile
        return JsonResponse({'username': profile.user.username,
                             'name': profile.name,
                             'bio': profile.bio,
                             'last_active': profile.last_active
                             }, status=200)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User is not authenticated'}, status=400)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError or KeyError:
            return JsonResponse({'error': 'Bad Request'}, status=400)

        profile = request.user.profile
        if 'username' in body:
            profile.user.username = body['username']
        if 'name' in body:
            profile.name = body['name']
        if 'bio' in body:
            profile.bio = body['bio']
        profile.save()

        return JsonResponse({'status': 'ok'}, status=200)

    def delete(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User is not authenticated'}, status=400)

        request.user.profile.delete()
        request.user.delete()
        return JsonResponse({'status': 'ok'}, status=200)
