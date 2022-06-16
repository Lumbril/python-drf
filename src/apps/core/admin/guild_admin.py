from apps.core.models.guild_models import *

from django.contrib import admin


@admin.register(Guild)
class GuildAdmin(admin.ModelAdmin):

    search_fields = ('name',)
    list_display = ('name',)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(GuildRank)
class GuildRankAdmin(admin.ModelAdmin):

    list_display = ('name_system', 'name', 'worth', 'opportunity_accept_application')
    list_filter = ('opportunity_accept_application', )


@admin.register(GuildPlayer)
class GuildPlayerAdmin(admin.ModelAdmin):

    list_display = ('guild', 'player', 'rank', 'active')
    list_filter = ('guild', 'player', 'rank', 'active')


@admin.register(GuildApplication)
class GuildApplicationAdmin(admin.ModelAdmin):

    list_display = ('type', 'status', 'date_created', 'to')
    list_filter = ('type', 'status', 'date_created', 'to')
