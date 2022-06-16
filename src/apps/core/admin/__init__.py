from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry

from django.contrib import admin

from .card_admin import *
from .chest_admin import *
from .guild_admin import *
from .player_admin import *
from .storage_admin import *
from .notification_admin import *
from .auction_admin import *


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Django sessions"""

    fields = ('session_key', 'session_data', 'expire_date',)
    list_display = ('session_key', 'get_decoded', 'expire_date',)
    search_fields = ('session_key',)
    date_hierarchy = 'expire_date'
    ordering = ('-expire_date',)


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Django log admin"""

    list_display = ('get_message', 'user', 'action_time',)
    search_fields = ('user', 'object_repr', 'change_message',)
    list_filter = ('action_flag', 'content_type',)
    autocomplete_fields = ('user',)
    date_hierarchy = 'action_time'
    ordering = ('-action_time',)

    def get_message(self, obj): return obj

    get_message.short_description = 'message'
