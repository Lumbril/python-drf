from django.contrib import admin

from .models import *


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):

    list_display = ('title', 'abbreviation',)
    search_fields = ('title', )


@admin.register(Translate)
class TranslateAdmin(admin.ModelAdmin):

    list_display = ('key_translate', 'translate', 'language')
    list_filter = ('language',)
    search_fields = ('key_translate',)
