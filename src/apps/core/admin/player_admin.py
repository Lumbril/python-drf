from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model

from apps.core.models import CardSet, Level

from django.contrib import admin

import copy


UserModel = get_user_model()


class TokenInline(admin.TabularInline):

    model = Token
    extra = 0


class CardSetInline(admin.TabularInline):

    model = CardSet
    extra = 0


@admin.register(UserModel)
class UserAdmin(BaseUserAdmin):

    list_display = ('auth_id', 'username', 'email', 'is_staff', 'is_active',)
    filter_horizontal = ('groups', 'user_permissions',)
    list_display_links = ('username',)

    def get_inlines(self, request, obj=None):
        if not obj:
            return self.inlines
        return [TokenInline, CardSetInline]

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        fieldsets = list(copy.deepcopy(self.fieldsets))
        fieldsets.insert(2, ('Player Info', {'fields': ('auth_id', 'icon', 'enter_ticket', 
                                                        'level', 'personal_exp', 'card_exp')}),)
        return fieldsets


@admin.register(CardSet)
class CardSetAdmin(admin.ModelAdmin):

    list_display = ('user', 'card', 'count')
    list_filter = ('date_deleted',)
    search_fields = ('user__username', 'card__content_object__name', 'card__content_object__type__name')


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):

    list_display = ('level', 'exp')
    search_fields = ('level',)
