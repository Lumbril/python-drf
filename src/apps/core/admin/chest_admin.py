from apps.core.models.chest_models import *
from apps.core.models.card_models import *

from django.utils.html import format_html

from django.contrib import admin


@admin.register(Chest)
class ChestAdmin(admin.ModelAdmin):
    """Сундук"""

    filter_horizontal = ('items',)
    list_display = ('name', 'type', 'purchase', 'sale', 'drop')
    list_filter = ('type',)

    def drop(self, obj):
        return format_html('<br>'.join([str(item) for item in obj.items.all()]))

    def purchase(self, obj): return format_html(
        '<span">{0}: {1}</span>', obj.currency_purchase, obj.amount_purchase)

    def sale(self, obj): return format_html(
        '<span">{0}: {1}</span>', obj.currency_sale, obj.amount_sale)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "type":
            kwargs["queryset"] = CardType.objects.filter(
                content_type__model=self.model.__name__.lower()
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Drop)
class DropAdmin(admin.ModelAdmin):
    """Элемент сундука"""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "card":
            user_warrior = WarriorCard.objects.filter(base=False)
            user_weapon = WeaponCard.objects.filter(base=False)
            user_armor = ArmorCard.objects.filter(base=False)
            kwargs["queryset"] = Card.objects.exclude(
                content_type__model=WarriorCard.__name__.lower(),
                object_id__in=user_warrior
            ).exclude(
                content_type__model=WeaponCard.__name__.lower(),
                object_id__in=user_weapon
            ).exclude(
                content_type__model=ArmorCard.__name__.lower(),
                object_id__in=user_armor
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Отвечает за набор из которого выпадет предмет"""

    filter_horizontal = ('items',)
