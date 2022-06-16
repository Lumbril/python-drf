from apps.core.models.notification_models import *

from django.contrib import admin


@admin.register(Notification)
class NotificationsAdmin(admin.ModelAdmin):

    list_display = ('user', 'header', 'author', 'date_departure', 'date_reading', 'date_deleted')
    list_filter = ('header', 'date_departure', 'date_reading', 'date_deleted')
    search_fields = ('user', )
