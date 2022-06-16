from django.contrib import admin

from .models import ChatLog


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):

    search_fields = ('guild__name', 'guild__tag', 'user__username')
    list_display = ('guild', 'user', 'time')
