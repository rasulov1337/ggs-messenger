from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=70)
    # avatar = models.ImageField(upload_to='uploads/images', default='default-avatar.png')
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    # objects = ProfileManager()

    def __str__(self):
        return self.name


class Chat(models.Model):
    name = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ChatParticipant(models.Model):
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    has_admin_rights = models.BooleanField(default=False)

    def __str__(self):
        return self.profile.user.username


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    text = models.TextField(max_length=500)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
