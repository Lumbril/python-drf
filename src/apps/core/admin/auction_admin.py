from django.utils.html import format_html

from apps.core.models.auction_models import *

from django.contrib import admin


@admin.register(AuctionLot)
class AuctionLotAdmin(admin.ModelAdmin):

    list_display = ('lot', 'user', 'currency', 'cost', 'date_created', 'date_edited', 'date_deleted')
    list_filter = ('currency', 'date_deleted')
    search_fields = ('user__username',)
