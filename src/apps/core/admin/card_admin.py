from django.contrib.contenttypes.models import ContentType

from django.utils.html import format_html

from apps.core.models.card_models import *
from apps.core.models import Chest

from django.contrib import admin

import copy


@admin.register(DamageType)
class DamageTypeAdmin(admin.ModelAdmin):
    """Тип урона"""

    search_fields = ('name',)
    list_display = ('name',)
    fields = ('name',)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):

    search_fields = ('name', 'system_name',)
    list_display = ('name', 'system_name',)
    fields = ('name', 'system_name',)


@admin.register(CardType)
class CardTypeAdmin(admin.ModelAdmin):
    """Тип карты"""

    list_display = ('name', 'system_name', 'rank_evo', 'display_preview',
                    'content_type', 'combat_card', 'damage_type',)
    fields = ('name', 'system_name', 'description', 'content_type', 
              'rank', 'damage_type', 'combat_card', 'icon', 'preview')
    list_filter = ('damage_type',)
    readonly_fields = ('preview',)
    search_fields = ('name',)
    models_for_content_type = (
        WarriorCard, WeaponCard, Chest,
        PotionCard, ArmorCard, Ticket
    )

    def rank_evo(self, obj):
        rank = None
        if obj.content_type.model == WarriorCard.__name__.lower():
            rank = obj.rank
        return format_html(str(rank) if rank else '#')

    def preview(self, obj): return format_html(
            '<a href="{0}" target="_blank">'
            '<img src="{0}" height="400"></a>', obj.get_icon()) if obj.get_icon() else '-'

    def display_preview(self, obj): return format_html(
            '<a href="{0}" target="_blank">'
            '<img src="{0}" height="100"></a>', obj.get_icon()) if obj.get_icon() else '-'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "content_type":
            kwargs["queryset"] = ContentType.objects.filter(model__in=[model.__name__.lower()
                                                                       for model in self.models_for_content_type])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    """Стихия"""

    list_display = ('name', 'display_preview', 'system_name', 'groups')
    fields = ('name', 'icon', 'preview', 'system_name', 'groups')
    readonly_fields = ('preview',)
    search_fields = ('name', 'system_name')

    def preview(self, obj): return format_html(
        '<a href="{0}" target="_blank">'
        '<img src="{0}" height="400"></a>', obj.get_icon()) if obj.get_icon() else '-'

    def display_preview(self, obj): return format_html(
        '<a href="{0}" target="_blank">'
        '<img src="{0}" height="100"></a>', obj.get_icon()) if obj.get_icon() else '-'


@admin.register(SpecialType)
class SpecialTypeAdmin(admin.ModelAdmin):
    """Виды особых эффектов"""

    list_display = ('name', 'system_name', 'to_enemy', 'display_preview')
    search_fields = ('name', 'system_name', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj): return format_html(
        '<a href="{0}" target="_blank">'
        '<img src="{0}" height="400"></a>', obj.get_icon()) if obj.get_icon() else '-'

    def display_preview(self, obj): return format_html(
        '<a href="{0}" target="_blank">'
        '<img src="{0}" height="100"></a>', obj.get_icon()) if obj.get_icon() else '-'


@admin.register(Special)
class SpecialAdmin(admin.ModelAdmin):
    """Особенный эффект"""

    search_fields = ('type__name', 'type__system_name')

    def get_list_display(self, obj):
        list_display = ['type', 'value', 'percentages', 'duration']
        command = lambda obj: format_html(f'<p>{"На противника" if obj.type.to_enemy else "На себя"}</p>')
        command.short_description = 'Действует'
        list_display.insert(1, command)
        return list_display


class AbstractCardAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {'fields': ('name', 'type', 'currency_purchase', 'amount_purchase',
                           'currency_sale', 'amount_sale', 'icon', 'preview',)}),
        ('Dates', {'fields': ('date_created', 'date_edited', 'date_deleted',)}),
    )
    list_display = ('name', 'type', 'purchase', 'sale', 'display_preview', 'date_edited', 'date_deleted',)
    readonly_fields = ('preview', 'date_created',)
    search_fields = ('name', 'icon',)
    list_filter = ('type',)
    date_hierarchy = 'date_edited'
    ordering = ('-date_edited',)

    def preview(self, obj): return format_html(
        '<a href="{0}" target="_blank">'
        '<img src="{0}" height="400"></a>', obj.get_icon()) if obj.get_icon() else '-'

    def display_preview(self, obj): return format_html(
        '<a href="{0}" target="_blank">'
        '<img src="{0}" height="100"></a>', obj.get_icon()) if obj.get_icon() else '-'

    def purchase(self, obj): return format_html(
        '<span">{0}: {1}</span>', obj.currency_purchase, obj.amount_purchase)

    def sale(self, obj): return format_html(
        '<span">{0}: {1}</span>', obj.currency_sale, obj.amount_sale)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "type":
            kwargs["queryset"] = CardType.objects.filter(content_type__model=self.model.__name__.lower())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PotionSize)
class PotionSizeAdmin(admin.ModelAdmin):
    """Размер зелья"""

    search_fields = ('name',)
    list_display = ('name',)
    fields = ('name', 'system_name')


@admin.register(PotionCard)
class PotionCardAdmin(AbstractCardAdmin):
    """Эликсир"""

    filter_horizontal = ('specials',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(copy.deepcopy(self.fieldsets))
        fieldsets[0][1]['fields'] = ('name', 'type', 'currency_purchase', 'amount_purchase',
                                     'currency_sale', 'amount_sale', 'icon', 'preview',)
        fieldsets.insert(1, ('Characteristics', {'fields': ('level', 'size', 'specials',)}), )
        return fieldsets

    def get_list_filter(self, request):
        return self.list_filter + ('specials',)


@admin.register(WeaponCard)
class WeaponCardAdmin(AbstractCardAdmin):
    """Оружие"""

    filter_horizontal = ('specials',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(copy.deepcopy(self.fieldsets))
        fieldsets.insert(1, ('Characteristics',
                             {'fields': ('damage', 'element', 'base', 'req_agility', 'req_strength',
                                         'req_vitality', 'critical_chance', 'req_intelligence',)}
                             ),
                         )
        fieldsets.insert(2, ('Ratio',
                             {'fields': ('ratio_agility', 'ratio_strength', 'ratio_intelligence', 'ratio_vitality')}
                             ),
                         )
        fieldsets.insert(3, ('Ability',
                             {'fields': ('ability_name', 'specials', 'ability_cooldown', 'attack_immediately')}
                             ),
                         )
        return fieldsets

    def get_list_display(self, request):
        name = lambda obj: str(obj)
        name.short_description = 'Название'

        list_display = list(copy.deepcopy(self.list_display))
        list_display[0] = name
        return list_display

    def get_list_filter(self, request):
        return self.list_filter + ('element', 'base',)


@admin.register(ArmorCard)
class ArmorCardAdmin(AbstractCardAdmin):
    """Броня"""

    filter_horizontal = ('specials',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(copy.deepcopy(self.fieldsets))
        fieldsets.insert(1, ('Characteristics',
                             {'fields': ('element', 'base', 'req_agility', 'req_strength',
                                         'req_vitality', 'req_intelligence', 'damage_reduction')}
                             ),
                         )
        fieldsets.insert(3, ('Ability',
                             {'fields': ('ability_name', 'specials', 'ability_cooldown')}
                             ),)
        return fieldsets

    def get_list_display(self, request):
        name = lambda obj: str(obj)
        name.short_description = 'Название'

        list_display = list(copy.deepcopy(self.list_display))
        list_display[0] = name
        return list_display

    def get_list_filter(self, request):
        return self.list_filter + ('element', 'specials', 'base',)


@admin.register(WarriorCard)
class WarriorCardAdmin(AbstractCardAdmin):
    """Воин"""

    filter_horizontal = ('specials',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(copy.deepcopy(self.fieldsets))
        fieldsets[0][1]['fields'] = ('name', 'type', 'level', 'experience', 'progress',
                                     'currency_purchase', 'amount_purchase',
                                     'currency_sale', 'amount_sale', 'icon', 'preview',)
        fieldsets.insert(1, ('Characteristics',
                             {'fields': ('defense', 'agility', 'potential', 'strength',
                                         'vitality', 'intelligence',)}
                             ),
                         )
        fieldsets.insert(2, ('Additionals',
                             {'fields': ('base', 'primary_element', 'secondary_element', 'specials')}
                             ),
                         )
        fieldsets[3][1]['fields'] += ('available_from',)
        return fieldsets

    def get_list_filter(self, request):
        return self.list_filter + ('primary_element', 'secondary_element', 'specials', 'base',)

    def get_list_display(self, request):
        name = lambda obj: str(obj)
        name.short_description = 'Название'

        list_display = list(copy.deepcopy(self.list_display))
        list_display[0] = name
        list_display.insert(2, 'level')
        list_display.insert(3, 'experience')
        list_display.insert(-2, 'available_from')
        return list_display


@admin.register(Evolution)
class EvolutionAdmin(admin.ModelAdmin):
    
    search_fields = ('base_type__name', 'next_type__name')
    list_filter = ('base_type', 'next_type',)
    filter_horizontal = ('specials',)
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = list()
        fieldsets.insert(1, ('Types',
                             {'fields': ('base_type', 'next_type')}
                             ),
                         )
        fieldsets.insert(1, ('Requirements',
                             {'fields': ('req_agility', 'req_defense', 'req_strength',
                                         'req_vitality', 'req_intelligence',)}
                             ),
                         )
        fieldsets.insert(2, ('Delta',
                             {'fields': ('delta_agility', 'delta_defense', 'delta_strength',
                                         'delta_vitality', 'delta_intelligence',)}
                             ),
                         )
        fieldsets.insert(3, ('Specials',
                             {'fields': ('specials',)}
                             ),
                         )
        return fieldsets

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "base_type":
            kwargs["queryset"] = CardType.objects.filter(content_type__model__iexact=WarriorCard.__name__.lower())
        if db_field.name == "next_type":
            kwargs["queryset"] = CardType.objects.filter(content_type__model__iexact=WarriorCard.__name__.lower())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(TicketCurrency)
class TicketCurrencyAdmin(admin.ModelAdmin):

    fields = ('currency', 'amount',)
    list_display = ('currency', 'amount',)
    search_fields = ('currency__name', 'currency__system_name', 'amount',)
    list_filter = ('currency',)


@admin.register(TicketCard)
class TicketCardAdmin(admin.ModelAdmin):

    fields = ('card', 'amount',)
    list_display = ('card', 'amount',)
    search_fields = ('card__content_object__type__name', 'card__content_object__name', 
                     'card__content_object__type__system_name', 'amount',)
    list_filter = ('card',)


@admin.register(Ticket)
class TicketAdmin(AbstractCardAdmin):
    """Билет"""

    filter_horizontal = ('currencies', 'cards',)

    def get_list_filter(self, request):
        list_filter = ('currencies',)
        return self.list_filter + list_filter

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(copy.deepcopy(self.fieldsets))
        fieldsets[0][1]['fields'] = ('name', 'type', 'base', 'currency_purchase', 'amount_purchase',
                                     'currency_sale', 'amount_sale', 'icon', 'preview',)
        fieldsets[1][1]['fields'] = ('date_created', 'date_edited', 'date_deleted', 'date_activation',)
        fieldsets.insert(1, ('Rewards', {'fields': ('currencies', 'cards',)}))
        return fieldsets

    def get_list_display(self, request):
        name = lambda obj: str(obj)
        name.short_description = 'Название'

        list_display = list(copy.deepcopy(self.list_display))
        list_display[0] = name
        list_display.insert(-2, 'date_activation')
        return list_display
