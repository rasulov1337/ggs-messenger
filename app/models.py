from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=70)
    # avatar = models.ImageField(upload_to='uploads/images', default='default-avatar.png')
    bio = models.TextField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    # objects = ProfileManager()

    def __str__(self):
        return self.name


class ChatManager(models.Manager):
    def get_chats_of_user(self, user_id):
        profile = Profile.objects.get(user_id=user_id)
        return Chat.objects.filter(chatparticipant__profile=profile).order_by('-created_at')

    def search_chats_of_user(self, user_id, query):
        chats = self.get_chats_of_user(user_id).filter(text__icontains=query)
        return {'chats': [{'id': chat.id, 'name': chat.name} for chat in chats]}


class Chat(models.Model):
    name = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ChatManager()

    def __str__(self):
        return self.name


class ChatParticipant(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    has_admin_rights = models.BooleanField(default=False)

    def __str__(self):
        return self.profile.user.username

    class Meta:
        unique_together = (('chat', 'profile'),)


class MessageManager(models.Manager):
    def get_messages_of_chat(self, chat_id: int):
        return Message.objects.filter(chat__id=chat_id).order_by('-sent_at')

    def search_messages_in_chat(self, chat_id: int, query):
        messages = self.get_messages_of_chat(chat_id).filter(text__icontains=query)[:50]
        result = {'messages': [{'id': message.id, 'text': message.text} for message in messages]}
        return result


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    text = models.TextField(max_length=500)
    sent_at = models.DateTimeField(auto_now_add=True)

    objects = MessageManager()

    def __str__(self):
        return self.text
