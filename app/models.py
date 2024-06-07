from django.db import models
from django.contrib.auth.models import User


class Profiles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=70)
    # avatar = models.ImageField(upload_to='uploads/images', default='default-avatar.png')
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    # objects = ProfileManager()

    def __str__(self):
        return self.name


class Chats(models.Model):
    name = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ChatParticipants(models.Model):
    chat = models.OneToOneField(Chats, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profiles, on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.user.username


class Messages(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
