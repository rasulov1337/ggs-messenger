from django.urls import path

from . import views

urlpatterns = [
    path('messages/get-cent-token', views.get_centrifugo_token, name='get-cent-token'),
    path('messages/edit', views.edit_message, name='edit-message'),
    path('messages/delete', views.delete_message, name='delete-message'),
    path('messages/send', views.send_message, name='send-message'),
    path('auth/login', views.login, name='login'),
    path('auth/register', views.register, name='register'),
    path('auth/logout', views.logout, name='logout'),
    path('profiles/self', views.SelfProfileView.as_view(), name='self-profile'),
    path('profiles/<int:profile_id>', views.get_profile_info, name='get-profile-info'),
    path('', views.index, name="index"),
]
