from django.urls import path

from . import views

urlpatterns = [
    path('auth/login', views.login, name='login'),
    path('auth/register', views.register, name='register'),
    path('auth/logout', views.logout, name='logout'),
    path('chats', views.get_chats, name='get-chats'),
    path('chats/search', views.search_chats, name='search-chats'),
    path("", views.index, name="index"),
]
