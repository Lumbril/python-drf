from django.utils.html import format_html

from apps.core.models import Storage

from django.contrib import admin


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):

    list_display = ('media_id', 'name', 'display_preview',)
    fields = ('media_id', 'name', 'url', 'preview',)
    list_display_links = ('name',)
    readonly_fields = ('preview',)
    search_fields = ('name',)

    def preview(self, obj): return format_html(
        '<a href="{0}" target="_blank">'
        '<img src="{0}" height="400"></a>', obj.get_icon()) if obj.get_icon() else '-'

    def display_preview(self, obj): return format_html(
        '<a href="{0}" target="_blank">'
        '<img src="{0}" height="100"></a>', obj.get_icon()) if obj.get_icon() else '-'
