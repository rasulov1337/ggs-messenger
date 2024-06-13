from django.urls import path

from . import views

urlpatterns = [
    path('auth/login', views.login, name='login'),
    path('auth/register', views.register, name='register'),
    path('auth/logout', views.logout, name='logout'),

    path('chats', views.ChatView.as_view(), name='get-chats'),
    path('chats', views.ChatView.as_view(), name='create-chat'),
    path('chats/search-chat', views.ChatView.as_view(), name='search-chats'),
    path('chats/<int:chat_id>/search-messages', views.ChatView.as_view(), name='search-messages'),
    path('chats/<int:chat_id>', views.ChatView.as_view(), name='get-messages'),
    path('chats/<int:chat_id>', views.ChatView.as_view(), name='delete-message'),
    path('', views.index, name='index'),
]
