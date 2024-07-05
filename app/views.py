import json
import time  # Token generation

import jwt  # Token generation

from cent import Client, PublishRequest  # Centrifugo
from django.contrib import auth
from django.db import IntegrityError
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
            return JsonResponse({'status': 'ok'}, status=200)
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


class ChatListView(View):
    model = Chat

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User is not authenticated'}, status=400)

        if request.method == 'GET':
            if request.GET.get('search', None) is not None:
                return self.search_chats(request)
            return self.get_chat_list(request)
        elif request.method == 'POST':
            return self.create_chat(request)
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    def get_chat_list(self, request):
        chats = Chat.objects.get_chats_of_user(request.user.id)
        data = {'chats': [{'id': chat.id, 'name': chat.name} for chat in chats]}
        return JsonResponse(data)

    def search_chats(self, request):
        query = request.GET.get('q', None)
        if query is None:
            return JsonResponse({'result': []})
        return JsonResponse(Chat.objects.search_chats_of_user(request.user.id, query))

    def create_chat(self, request):
        try:
            data = json.loads(request.body)
            chat_name = data.get('name')
            usernames = data.get('members', [])

            if not chat_name or not usernames:
                return JsonResponse({'error': 'Missing chat name or usernames.'}, status=400)

            chat = Chat.objects.create(name=chat_name)

            for username in usernames:
                try:
                    profile = Profile.objects.get(user__username=username)
                    ChatParticipant.objects.create(chat=chat, profile=profile)
                except Profile.DoesNotExist:
                    return JsonResponse({'error': f'Profile with username {username} does not exist.'}, status=400)

            return JsonResponse({'id': chat.id, 'name': chat.name}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)


class ChatDetailView(View):
    model = Chat

    def dispatch(self, request, *args, **kwargs):
        chat_id = kwargs.get('chat_id')
        if request.method == 'GET':
            return self.get_chat_messages(request, chat_id)
        elif request.method == 'DELETE':
            return self.delete_chat(request, chat_id)
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

    def get_chat_messages(self, request, chat_id):
        messages = Message.objects.get_messages_of_chat(chat_id)
        data = {'chats': [{'id': message.id, 'text': message.text} for message in messages]}
        return JsonResponse(data)

    def delete_chat(self, request, chat_id):
        profile = get_object_or_404(Profile, user=request.user)

        chat = get_object_or_404(Chat, id=chat_id)
        participant = ChatParticipant.objects.filter(chat=chat, profile=profile, has_admin_rights=True).first()

        if not participant:
            return JsonResponse({'error': 'You do not have permission to delete this chat.'}, status=403)

        chat.delete()
        return JsonResponse({'status': 'Chat deleted successfully'})


class MessageListView(View):
    model = Message

    def dispatch(self, request, *args, **kwargs):
        chat_id = kwargs.get('chat_id')
        if request.method == 'GET':
            return self.search_messages_in_chat(request, chat_id)
        elif request.method == 'POST':
            return self.send_message(request)
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

    def search_messages_in_chat(self, request, chat_id):
        query = request.GET.get('q', None)
        if query is None:
            return JsonResponse({'result': []})

        return JsonResponse(Message.objects.search_messages_in_chat(chat_id, query))

    def send_message(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User is not authenticated'}, status=400)

        api_url = settings.CENTRIFUGO_API_URL
        api_key = settings.CENTRIFUGO_API_KEY

        try:
            body = json.loads(request.body)

            client = Client(api_url, api_key)  # TODO: Возможно не стоит каждый раз создавать клиент
            publist_request = PublishRequest(
                channel=str(body['chatId']),
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


class MessageDetailView(View):
    model = Message

    def dispatch(self, request, *args, **kwargs):
        message_id = kwargs.get('message_id')
        if request.method == 'DELETE':
            return self.delete_message(request, message_id)
        elif request.method == 'PATCH':
            return self.edit_message(request, message_id)
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

    def edit_message(self, request, message_id: int) -> JsonResponse:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User is not authenticated'}, status=400)

        api_url = settings.CENTRIFUGO_API_URL
        api_key = settings.CENTRIFUGO_API_KEY

        try:
            body = json.loads(request.body)

            client = Client(api_url, api_key)  # TODO: Возможно не стоит каждый раз создавать клиент
            request = PublishRequest(
                channel=str(body['chatId']),
                data={
                    'type': 'edit_message',
                    'data': {
                        'messageId': message_id,
                        'text': body['text'],
                    }
                })
            client.publish(request)

            # Update the message
            Message.objects.filter(pk=message_id).update(text=body['text'])
        except json.JSONDecodeError or KeyError:
            return JsonResponse({'error': 'Bad Request'}, status=400)
        return JsonResponse({'status': 'ok'}, status=200)

    def delete_message(self, request, message_id: int) -> JsonResponse:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User is not authenticated'}, status=400)

        try:
            body = json.loads(request.body)

            # Delete the message from the database
            msg = Message.objects.filter(pk=message_id)
            if not msg.exists():
                return JsonResponse({'error': 'Message does not exist'}, status=400)

            msg.delete()

            # Send a message to Centrifugo to delete the message from the chat
            api_url = settings.CENTRIFUGO_API_URL
            api_key = settings.CENTRIFUGO_API_KEY

            client = Client(api_url, api_key)  # TODO: Возможно не стоит каждый раз создавать клиент
            request = PublishRequest(
                channel=str(body['chatId']),
                data={
                    'type': 'delete_message',
                    'data': {
                        'messageId': message_id
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


def search_profile(request):
    query = request.GET.get('q', None)
    if query is None:
        return JsonResponse({'result': []})
    profiles = Profile.objects.filter(user__username__icontains=query).order_by('user__username')
    return JsonResponse(
        {'profiles': [{'username': profile.user.username, 'name': profile.name} for profile in profiles]})


class SelfProfileView(View):
    model = Profile

    def get(self, request):
        # Получить список участников чата
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User is not authenticated'}, status=400)

        profile = request.user.profile
        return JsonResponse(
            {
                'response':
                    {'username': profile.user.username,
                     'name': profile.name,
                     'bio': profile.bio,
                     'last_active': profile.last_active
                     }
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


class ChatMemberView(View):
    model = Profile

    # TODO: ДОБАВИТЬ ПРОВЕРКУ НА АВТОРСТВА ГРУППОЙ
    # ПОКА ПОХУЙ ПОТОМУ ЧТО ВРЕМЕНИ МАЛО

    def get(self, request, chat_id: int):  # Returns all chat members
        members = ChatParticipant.objects.filter(chat_id=chat_id)
        response = [
            {'name': i.profile.name,
             'username': i.profile.user.username,
             'id': i.profile.id,
             } for i in members
        ]
        return JsonResponse({'members': response}, status=200)

    def post(self, request, chat_id):  # Add users to a chat
        chat = get_object_or_404(Chat, id=chat_id)
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError or KeyError:
            return JsonResponse({'error': 'Bad Request'}, status=400)

        profiles_to_add = [get_object_or_404(Profile, user__username=username) for username in body.get('members')]
        for profile in profiles_to_add:
            try:
                ChatParticipant.objects.create(chat=chat, profile=profile).save()
            except IntegrityError:
                return JsonResponse({'error': 'User already exists'}, status=400)

        return JsonResponse({'status': 'ok'}, status=200)

    def delete(self, request, chat_id):  # Deletes user from chat
        chat = get_object_or_404(Chat, id=chat_id)
        try:
            ChatParticipant.objects.get(chat=chat, profile__user__username=request.GET.get('username')).delete()
        except ChatParticipant.DoesNotExist:
            return JsonResponse({'error': 'User does not belong to the chat'}, status=400)
        return JsonResponse({'status': 'ok'}, status=200)
