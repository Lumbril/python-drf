from rest_framework.pagination import PageNumberPagination

from django_filters import rest_framework as drf_filters
from django_filters.constants import EMPTY_VALUES

from apps.core.models import (
    AbstractCard, WeaponCard,
    PotionCard, WarriorCard,
    ArmorCard, Chest, Ticket
)
from django.db import models


class PaginationDefault(PageNumberPagination):

    page_size = 20
    max_page_size = 300


class CardsFilterBackend(drf_filters.DjangoFilterBackend):

    enum_content_type = {
        'warriors': 'warriorcard',
        'weapons': 'weaponcard',
        'armors': 'armorcard',
        'potions': 'potioncard',
        'ticket': 'ticket',
        'chests': 'chest'
    }

    def get_filterset_kwargs(self, request, queryset, view):
        kwargs = super().get_filterset_kwargs(request, queryset, view)

        if kwargs['data'] is not None and kwargs['data'].get('type',) is not None:
            kwargs['data']._mutable = True
            filter_kwargs = kwargs['data']['type'].split(',')
            args = list()
            for arg in filter_kwargs:
                if arg in list(self.enum_content_type.keys()):
                    args.append(self.enum_content_type[arg])
                    continue
                args.append(arg)
            kwargs['data']['type'] = ','.join(args)
        kwargs['data']._mutable = False

        return kwargs


class AbstractCardFilter(drf_filters.FilterSet):

    name = drf_filters.CharFilter(field_name='name', lookup_expr='contains')
    type = drf_filters.CharFilter(field_name='type__name', lookup_expr='contains')

    class Meta:
        model = AbstractCard
        fields = ('name', 'type',)


class PotionFilter(drf_filters.FilterSet):

    size = drf_filters.BaseInFilter(field_name='size')

    class Meta:
        model = PotionCard
        fields = ('size',)


class WeaponFilter(drf_filters.FilterSet):

    element = drf_filters.BaseInFilter(field_name='element')
    base = drf_filters.BaseInFilter(field_name='base')

    class Meta:
        model = WeaponCard
        fields = ('element', 'base')


class ArmorFilter(drf_filters.FilterSet):
    
    element = drf_filters.BaseInFilter(field_name='element')
    base = drf_filters.BaseInFilter(field_name='base')

    class Meta:
        model = ArmorCard
        fields = ('element', 'base')


class WarriorFilter(drf_filters.FilterSet):

    primary_element = drf_filters.BaseInFilter(field_name='primary_element')
    secondary_element = drf_filters.BaseInFilter(field_name='secondary_element')
    base = drf_filters.BaseInFilter(field_name='base')

    class Meta:
        model = WarriorCard
        fields = ('primary_element', 'secondary_element', 'base')


class TicketFilter(drf_filters.FilterSet):
    
    base = drf_filters.BaseInFilter(field_name='base')

    class Meta:
        model = Ticket
        fields = ('base',)


class CardTypeFieldFilter(drf_filters.Filter):

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        value_list = value.split(",")
        qs = super().filter(qs, value_list)
        return qs


class PlayerCardTypeFilter(drf_filters.FilterSet):

    def filter_queryset(self, queryset):
        for name, value in self.form.cleaned_data.items():
            if name == 'search' and value:
                for instance in queryset:
                    if value[0].lower() not in instance.card.content_object.name.lower() \
                            and value[0].lower() not in instance.card.content_object.type.name.lower():
                        queryset = queryset.exclude(pk=instance.pk)
            elif name == 'type':
                queryset = self.filters[name].filter(queryset, value)
            elif name == 'primary_element' and value:
                queryset = queryset.filter(card__content_type__model=WarriorCard.__name__.lower())
                for instance in queryset:
                    if instance.card.content_object.primary_element.id not in [int(pk) for pk in value]:
                        queryset = queryset.exclude(pk=instance.pk)
            elif name == 'element' and value:
                queryset = queryset.filter(card__content_type__model__in=(WeaponCard.__name__.lower(),
                                                                          ArmorCard.__name__.lower()))
                for instance in queryset:
                    if instance.card.content_object.element.id not in [int(pk) for pk in value]:
                        queryset = queryset.exclude(pk=instance.pk)
            elif name == 'size' and value:
                queryset = queryset.filter(card__content_type__model=PotionCard.__name__.lower())
                for instance in queryset:
                    if instance.card.content_object.size.id not in [int(pk) for pk in value]:
                        queryset = queryset.exclude(pk=instance.pk)
            elif name == 'card_type' and value:
                queryset = queryset.filter(card__content_type__model=Chest.__name__.lower())
                for instance in queryset:
                    if instance.card.content_object.type.id not in [int(pk) for pk in value]:
                        queryset = queryset.exclude(pk=instance.pk)
            elif (name == 'is_auction') and (value is not None):
                boolean = True if value[0].lower() not in ('False', 'false', '0') else False

                for instance in queryset:
                    if instance.check_is_auction != boolean:
                        queryset = queryset.exclude(pk=instance.pk)
            elif (name == 'injured') and value:
                boolean = True if value[0].lower() not in ('False', 'false', '0') else False
                queryset = queryset.filter(card__content_type__model=WarriorCard.__name__.lower())
                for instance in queryset:
                    if instance.card.content_object.injured != boolean:
                        queryset = queryset.exclude(pk=instance.pk)
            assert isinstance(queryset, models.QuerySet), \
                "Expected '%s.%s' to return a QuerySet, but got a %s instead." \
                % (type(self).__name__, name, type(queryset).__name__)
        return queryset

    search = drf_filters.BaseInFilter('card_id', help_text='A search Term')
    type = CardTypeFieldFilter(field_name='card__content_type__model', help_text='Сортировка по таблицам',
                               label='Тип карты, через запятую без пробела', lookup_expr='in')
    primary_element = drf_filters.BaseInFilter('card_id')
    element = drf_filters.BaseInFilter('card_id')
    size = drf_filters.BaseInFilter('card_id')
    card_type = drf_filters.BaseInFilter('card_id', help_text='Сортировка для сундуков по типам карт')
    is_auction = drf_filters.BaseInFilter('is_auction', help_text='Сортировка по участию в аукционе')
    injured = drf_filters.BaseInFilter('card_id', help_text='Травмирована')

    class Meta:
        fields = ('type',)


class AuctionFilter(drf_filters.FilterSet):

    def filter_queryset(self, queryset):
        for name, value in self.form.cleaned_data.items():
            if name == 'search' and value:
                for instance in queryset:
                    if value[0].lower() not in instance.lot.card.content_object.name.lower() \
                            and value[0].lower() not in instance.lot.card.content_object.type.name.lower():
                        queryset = queryset.exclude(pk=instance.pk)
            elif name == 'type':
                queryset = self.filters[name].filter(queryset, value)
            elif name == 'primary_element' and value:
                queryset = queryset.filter(lot__card__content_type__model=WarriorCard.__name__.lower())
                for instance in queryset:
                    if instance.lot.card.content_object.primary_element.id not in [int(pk) for pk in value]:
                        queryset = queryset.exclude(pk=instance.pk)
            elif name == 'element' and value:
                queryset = queryset.filter(lot__card__content_type__model__in=(WeaponCard.__name__.lower(),
                                                                          ArmorCard.__name__.lower()))
                for instance in queryset:
                    if instance.lot.card.content_object.element.id not in [int(pk) for pk in value]:
                        queryset = queryset.exclude(pk=instance.pk)
            elif name == 'size' and value:
                queryset = queryset.filter(lot__card__content_type__model=PotionCard.__name__.lower())
                for instance in queryset:
                    if instance.lot.card.content_object.size.id not in [int(pk) for pk in value]:
                        queryset = queryset.exclude(pk=instance.pk)
            elif name == 'card_type' and value:
                queryset = queryset.filter(lot__card__content_type__model=Chest.__name__.lower())
                for instance in queryset:
                    if instance.lot.card.content_object.type.id not in [int(pk) for pk in value]:
                        queryset = queryset.exclude(pk=instance.pk)
            elif name == 'personal_lot' and value:
                boolean = True if value[0].lower() in ('true', '1') else False

                if boolean:
                    for instance in queryset:
                        if instance.personal_lot(self.request.user) != boolean:
                            queryset = queryset.exclude(pk=instance.pk)
            assert isinstance(queryset, models.QuerySet), \
                "Expected '%s.%s' to return a QuerySet, but got a %s instead." \
                % (type(self).__name__, name, type(queryset).__name__)
        return queryset

    search = drf_filters.BaseInFilter('lot__card_id', help_text='A search Term')
    type = CardTypeFieldFilter(field_name='lot__card__content_type__model', help_text='Сортировка по таблицам',
                               label='Тип карты, через запятую без пробела', lookup_expr='in')
    primary_element = drf_filters.BaseInFilter('lot__card_id')
    element = drf_filters.BaseInFilter('lot__card_id')
    size = drf_filters.BaseInFilter('lot__card_id')
    card_type = drf_filters.BaseInFilter('lot__card_id', help_text='Сортировка для сундуков по типам карт')
    personal_lot = drf_filters.BaseInFilter('user', help_text='Личный лот')

    class Meta:
        fields = ('type',)


class CardTypeFilter(drf_filters.FilterSet):

    type = CardTypeFieldFilter(field_name='content_type__model',
                               label='Тип карты, через запятую без пробела', lookup_expr='in')

    class Meta:
        fields = ('type',)


class GuildOpenFilter(drf_filters.FilterSet):

    open = drf_filters.BooleanFilter(field_name='type', label='Открытая гильдия')

    class Meta:
        fields = ('open',)


class ChestTypeFilter(drf_filters.FilterSet):

    card_type = drf_filters.BaseInFilter(field_name='type')

    class Meta:
        fields = ('card_type',)


class CombatCardFilter(drf_filters.FilterSet):

    combat_card = drf_filters.BooleanFilter(field_name='combat_card')

    class Meta:
        fields = ('combat_card',)


class UsernameFilter(drf_filters.FilterSet):

    username = drf_filters.BaseInFilter(field_name='username')

    class Meta:
        fields = ('username',)


class NotificationFilter(drf_filters.FilterSet):

    is_read = drf_filters.BaseInFilter(field_name='is_read')

    class Meta:
        fields = ('is_read',)
