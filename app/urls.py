from django.urls import path

from . import views

urlpatterns = [
    path('auth/login', views.login, name='login'),
    path('auth/register', views.register, name='register'),
    path('auth/logout', views.logout, name='logout'),

    path('chats', views.ChatListView.as_view(), name='chat-list'),
    path('chats/get-cent-token', views.get_centrifugo_token, name='get-cent-token'),
    path('chats/<int:chat_id>', views.ChatDetailView.as_view(), name='chat-detail'),
    path('chats/<int:chat_id>/messages', views.MessageListView.as_view(), name='messages-list'),
    path('chats/<int:chat_id>/messages/<int:message_id>', views.MessageDetailView.as_view(), name='message-detail'),
    path('', views.index, name='index'),
]
