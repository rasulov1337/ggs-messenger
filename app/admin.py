from django.contrib import admin
from . import models


admin.site.register(models.Profile)
admin.site.register(models.Message)
admin.site.register(models.Chat)
admin.site.register(models.ChatParticipant)