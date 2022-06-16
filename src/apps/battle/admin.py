from django.contrib import admin

from .models import *


class RoundInline(admin.StackedInline):

    model = BattleRound
    extra = 0


@admin.register(BattleLog)
class BattleLogAdmin(admin.ModelAdmin):

    search_fields = ('key', 'user1__username', 'user1__username')
    list_display = ('key', 'user1', 'user2', 'time')
    inlines = (RoundInline,)


@admin.register(BattleRound)
class BattleRoundsAdmin(admin.ModelAdmin):

    search_fields = ('battle__key', 'battle__user1__username', 'battle__user2__username')
