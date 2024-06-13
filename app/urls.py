from django.urls import path

from . import views

urlpatterns = [
    path('auth/login', views.login, name='login'),
    path('auth/register', views.register, name='register'),
    path('auth/logout', views.logout, name='logout'),
    path('messages/get-cent-token', views.get_centrifugo_token, name='get-cent-token'),
    path('messages/edit', views.edit_message, name='edit-message'),
    path('messages/delete', views.delete_message, name='delete-message'),
    path('messages/send', views.send_message, name='send-message'),
    path('chats', views.ChatsViews.as_view(), name='get-chats'),
    path('chats', views.ChatsViews.as_view(), name='create-chat'),
    path('chats/search-chat', views.ChatsViews.as_view(), name='search-chats'),
    path('chats/<int:chat_id>/search-messages', views.ChatsDetailsView.as_view(), name='search-messages'),
    path('chats/<int:chat_id>', views.ChatsDetailsView.as_view(), name='get-messages'),
    path('chats/<int:chat_id>', views.ChatsDetailsView.as_view(), name='delete-chat'),
    path('', views.index, name='index'),
]
