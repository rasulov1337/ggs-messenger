from django.urls import path

from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('auth/login', views.login, name='login'),
    path('auth/register', views.register, name='register'),
    path('auth/logout', views.logout, name='logout'),

    path('chats', views.ChatListView.as_view(), name='chat-list'),
    path('chats/get-cent-token', views.get_centrifugo_token, name='get-cent-token'),
    path('chats/<int:chat_id>', views.ChatDetailView.as_view(), name='chat-detail'),
    path('chats/<int:chat_id>/members', views.ChatMemberView.as_view(), name='messages-list'),
    path('chats/<int:chat_id>/messages', views.MessageListView.as_view(), name='messages-list'),
    path('chats/<int:chat_id>/messages/<int:message_id>', views.MessageDetailView.as_view(), name='message-detail'),

    path('profiles/self', views.SelfProfileView.as_view(), name='self-profile'),
    path('profiles/<int:profile_id>', views.get_profile_info, name='get-profile-info'),
    path('profiles/search', views.search_profile, name='search-profile'),
]

urlpatterns += staticfiles_urlpatterns()  # Works only in development mode
