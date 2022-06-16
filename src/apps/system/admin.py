from django.utils.html import format_html

from django.contrib import admin

from .models import *


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):

    search_fields = ('name',)
    list_display = ('name',)
    fields = ('name',)


@admin.register(SystemInfo)
class SystemInfoAdmin(admin.ModelAdmin):

    list_display = ('type', 'key', 'display_preview')
    list_filter = ('type', 'key', )

    def display_preview(self, icon):
        return format_html(
            '<a href="{0}" target="_blank">'
            '<img src="{0}" height="100"></a>', icon.get_icon()
        ) if icon.get_icon() else icon.get_text()
