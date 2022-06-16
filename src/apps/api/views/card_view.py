
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, filters, exceptions, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

from django.utils.decorators import method_decorator

from apps.api.serializers.card_serializer import *
from apps.api.service import (
    PotionFilter, WeaponFilter, ArmorFilter,
    CardsFilterBackend, CardTypeFilter,
    PaginationDefault, WarriorFilter,
    TicketFilter
)

from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema

from apps.core.models.card_models import *

from django.db.models import Prefetch, F
from django.db import transaction

from datetime import datetime

from broker import RpcClient
from packs import (
    IsEnoughBalance,
    Successful
)


class CardViewSet(GenericViewSet):
    """Список всех карт"""

    queryset = Card.objects.all()
    serializer_class = CardSerializer
    pagination_class = PaginationDefault

    @swagger_auto_schema(operation_summary="Карта по NFT-токену",
                         responses={status.HTTP_200_OK: CardSerializer})
    @action(methods=['post'], detail=False,
            permission_classes=[AllowAny],
            serializer_class=NFTCardSerializer)
    def nft(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        client = RpcClient()
        try:
            with transaction.atomic():
                card = client.call('payment', 'get_card', token)
                self.kwargs['pk'] = card.get('card_id')
        except exceptions.NotFound as e: raise e
        except Exception as e:
            raise exceptions.APIException(e)

        instance = self.get_object()
        serializer = CardSerializer(instance)
        return Successful(serializer.data)

    @swagger_auto_schema(operation_summary="Покупка карты")
    @action(methods=['post'], detail=True,
            serializer_class=CardPurchaseSerializer,
            permission_classes=[IsEnoughBalance])
    def purchase(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        def get_product():
            if instance.content_type.model in ('warriorcard', 'weaponcard', 'armorcard', 'ticket'):
                if not instance.content_object.base:
                    raise exceptions.NotFound('Not found card in store.')

                object = instance.content_object.clone()
                card = self.get_queryset().get(
                    content_type=object.card.content_type.id,
                    object_id=object.id
                )
                CardSet.objects.create(user=user, card=card, count=1)

            elif instance in user.get_cards_list():
                card_set = user.cards.get(card=instance)
                card_set.count += 1
                card_set.save(update_fields=['count'])
            else:
                CardSet.objects.create(user=user, card=instance, count=1)

            user.save()

        client = RpcClient()
        try:
            with transaction.atomic():
                get_product()
                client.call('auth', 'withdrawal', request.cost)
        except exceptions.ValidationError as e: raise e
        except exceptions.APIException as e: raise e
        except Exception as e:
            raise exceptions.APIException(e)

        return Successful()

    @swagger_auto_schema(operation_summary="Продажа карты")
    @action(methods=['delete'], detail=True,
            serializer_class=CardPurchaseSerializer)
    def sale(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        def sale_product():
            card = CardSet.objects.filter(user=user, card=instance.id, date_deleted__isnull=True)

            if not card.exists():
                raise exceptions.ValidationError({'detail': 'The card does not exist'})

            card = card.first()

            card.count -= 1

            if card.count == 0:
                if card.card.content_type.model == 'warriorcard':
                    warrior_card = WarriorCard.objects.get(id=card.card.object_id)
                    warrior_card.date_deleted = datetime.now()
                    warrior_card.save()
                elif card.card.content_type.model == 'armorcard':
                    armor_card = ArmorCard.objects.get(id=card.card.object_id)
                    armor_card.date_deleted = datetime.now()
                    armor_card.save()
                elif card.card.content_type.model == 'weaponcard':
                    weapon_card = WeaponCard.objects.get(id=card.card.object_id)
                    weapon_card.date_deleted = datetime.now()
                    weapon_card.save()
                elif card.card.content_type.model == 'ticket':
                    ticket_card = Ticket.objects.get(id=card.card.object_id)
                    ticket_card.date_deleted = datetime.now()
                    ticket_card.save()
                card.date_deleted = datetime.now()

            card.save()

            setattr(request, 'coin', dict(
                user=request.user.auth_id,
                currencies=[dict(
                    currency=card.card.content_object.currency_sale.system_name,
                    amount=card.card.content_object.amount_sale
                )]
            ))

        client = RpcClient()
        try:
            with transaction.atomic():
                sale_product()
                client.call('auth', 'accrual', request.coin)
        except exceptions.ValidationError as e: raise e
        except exceptions.APIException as e: raise e
        except Exception as e:
            raise exceptions.APIException(e)

        return Successful()


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о зельях"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о зелье"))
class PotionCardViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    """Список карт типа: 'Зелье'"""

    queryset = PotionCard.objects.exclude(date_deleted__lte=datetime.now())
    serializer_class = PotionCardSerializer
    pagination_class = PaginationDefault
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name', 'type__name')
    filterset_class = PotionFilter

    def get_queryset(self):
        if self.action == 'size':
            return PotionSize.objects.all()

        queryset_specials = Special.objects \
            .select_related('type') \
            .select_related('type__icon')

        queryset = PotionCard.objects.exclude(date_deleted__lte=datetime.now()) \
            .annotate(card_id=F('card__id')) \
            .select_related('icon') \
            .select_related('currency_purchase') \
            .select_related('currency_sale') \
            .select_related('type__content_type') \
            .select_related('type__icon') \
            .select_related('size') \
            .prefetch_related(Prefetch('specials', queryset=queryset_specials))

        return queryset

    @swagger_auto_schema(operation_summary="Выгрузка размера зелий")
    @action(methods=['get'], detail=False, url_path='size',
            filterset_class=None, search_fields=None,
            filter_backends=(DjangoFilterBackend,),
            serializer_class=PotionSizeSerializer,
            queryset=PotionSize.objects.all())
    def size(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Successful(serializer.data)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о броне"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о броне"))
class ArmorCardViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    """Список карт по имени типа: 'Броня'"""

    queryset = ArmorCard.objects.exclude(date_deleted__lte=datetime.now())
    serializer_class = ArmorCardSerializer
    pagination_class = PaginationDefault
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = ArmorFilter
    search_fields = ('name', 'type__name')

    def get_queryset(self):
        queryset_specials = Special.objects \
            .select_related('type') \
            .select_related('type__icon')

        queryset = ArmorCard.objects.exclude(date_deleted__lte=datetime.now()) \
            .annotate(card_id=F('card__id')) \
            .select_related('icon') \
            .select_related('currency_purchase') \
            .select_related('currency_sale') \
            .select_related('type__content_type') \
            .select_related('type__icon') \
            .select_related('element') \
            .select_related('element__icon') \
            .prefetch_related(Prefetch('specials', queryset=queryset_specials))

        return queryset


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о оружии"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о оружии"))
class WeaponCardViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    """Список карт типа: 'Оружие'"""

    queryset = WeaponCard.objects.exclude(date_deleted__lte=datetime.now())
    serializer_class = WeaponCardSerializer
    pagination_class = PaginationDefault
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = WeaponFilter
    search_fields = ('name', 'type__name')

    def get_queryset(self):
        queryset_specials = Special.objects \
            .select_related('type') \
            .select_related('type__icon')

        queryset = WeaponCard.objects.exclude(date_deleted__lte=datetime.now()) \
            .annotate(card_id=F('card__id')) \
            .select_related('icon') \
            .select_related('currency_purchase') \
            .select_related('currency_sale') \
            .select_related('type__content_type') \
            .select_related('type__icon') \
            .select_related('element') \
            .select_related('element__icon') \
            .prefetch_related(Prefetch('specials', queryset=queryset_specials))

        return queryset


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о войнах"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о войне"))
class WarriorCardViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    """Список карт типа: 'Воин'"""

    serializer_class = WarriorCardSerializer
    pagination_class = PaginationDefault
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = WarriorFilter
    search_fields = ('name', 'type__name')

    def get_evolutions_queryset(self):
        queryset_evolutions = Evolution.objects \
            .select_related('next_type', 'next_type__icon', 'base_type', 'base_type__icon')
        return queryset_evolutions

    def get_specials_queryset(self):
        queryset_specials = Special.objects \
            .select_related('type', 'type__icon')
        return queryset_specials

    def get_queryset(self):

        queryset = WarriorCard.objects.exclude(date_deleted__lte=datetime.now()) \
            .annotate(card_id=F('card__id')) \
            .select_related('icon') \
            .select_related('currency_purchase') \
            .select_related('currency_sale') \
            .select_related('type__content_type') \
            .select_related('type__icon') \
            .select_related('primary_element') \
            .select_related('primary_element__icon') \
            .select_related('secondary_element') \
            .select_related('secondary_element__icon') \
            .select_related('type') \
            .prefetch_related(Prefetch('type__base_types', queryset=self.get_evolutions_queryset())) \
            .prefetch_related(Prefetch('specials', queryset=self.get_specials_queryset())) \

        return queryset

    @action(methods=['get'], detail=True, serializer_class=EvolveSerializer)
    @swagger_auto_schema(operation_summary="Получение эволюций для карты")
    def evolution(self, request, *args, **kwargs):
        warrior = self.get_object()
        evolutions = self.get_evolutions_queryset().filter(base_type=warrior.type)\
            .prefetch_related(Prefetch('specials', self.get_specials_queryset()))
        serializer = EvolutionSerializer(evolutions, many=True, warrior=warrior)
        return Successful(serializer.data)

    @evolution.mapping.post
    @swagger_auto_schema(operation_summary="Метод для эволюции карты", request_body=EvolveSerializer)
    def evolve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        evolution = get_object_or_404(
            instance.get_next_evolutions(),
            pk=serializer.data.get('evolution_id', )
        )
        instance.evolve(evolution)
        return Successful()

    @action(methods=['post'], detail=True, serializer_class=StatsAddSerializer)
    @swagger_auto_schema(operation_summary="Получение вероятности для улучшения характеристик")
    def stats(self, request, *args, **kwargs):
        warrior = self.get_object()
        body = self.get_serializer(data=request.data)
        body.is_valid(raise_exception=True)
        serializer = StatsSerializer(instance=warrior, additional=body.data)
        return Successful(serializer.data)

    @action(methods=['post'], detail=True, serializer_class=StatsAddSerializer)
    @swagger_auto_schema(operation_summary="Улучшить характеристики")
    def upgrade(self, request, *args, **kwargs):
        warrior = self.get_object()
        if not warrior.card.first() in request.user.get_cards_list():
            raise exceptions.NotFound('User\'s warrior not found')
        if warrior.progress < 100:
            raise exceptions.ValidationError({'detail': 'Upgrade is not available'})
        body = self.get_serializer(data=request.data)
        body.is_valid(raise_exception=True)
        if sum(body.data.values()) > request.user.card_exp + warrior.experience:
            raise exceptions.ValidationError({'detail': 'Not enough card exp'})
        stats = StatsSerializer(instance=warrior, additional=body.data)
        stats = stats.data
        request.user.card_exp -= stats['cost']['user_card_exp']
        warrior.experience -= stats['cost']['warrior_exp']
        del stats['cost'], stats['ratio']
        stat = warrior.upgrade(stats)
        warrior.progress = round((warrior.progress - 100) / 2, 2)
        warrior.level += 1
        warrior.save()
        request.user.personal_exp += 10  # TODO: вынести в константы или конфиг
        request.user.save()
        return Successful(stat)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о стихиях"))
class ElementViewSet(mixins.ListModelMixin,
                     GenericViewSet):

    queryset = Element.objects.select_related('icon').all()
    serializer_class = ElementSerializer
    pagination_class = PaginationDefault


class CardTypeViewSet(mixins.ListModelMixin,
                      GenericViewSet):

    queryset = CardType.objects.select_related('icon', 'content_type')
    serializer_class = CardTypeSerializer
    pagination_class = PaginationDefault
    filter_backends = (CardsFilterBackend,)
    filterset_class = CardTypeFilter


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о билете"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о билете"))
class TicketViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):

    serializer_class = TicketSerializer
    pagination_class = PaginationDefault
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = TicketFilter
    search_fields = ('name', 'type__name')

    def get_queryset(self):
        if self.action == 'activation':
            return Card.objects.select_related('content_type').all()

        queryset_currencies = TicketCurrency.objects.select_related('currency').all()
        queryset_cards = TicketCard.objects.select_related('card', 'card__content_type').all()

        queryset = Ticket.objects.exclude(
            date_deleted__lte=datetime.now()) \
            .annotate(card_id=F('card__id')) \
            .select_related('icon') \
            .select_related('currency_purchase') \
            .select_related('currency_sale') \
            .select_related('type__content_type') \
            .select_related('type__icon') \
            .select_related('type') \
            .prefetch_related(
                Prefetch('currencies',
                         queryset=queryset_currencies)) \
            .prefetch_related(
                Prefetch('cards',
                         queryset=queryset_cards))

        return queryset

    @swagger_auto_schema(operation_summary="Активация билета",
                         responses={status.HTTP_200_OK: '{"successful": true}'})
    @action(methods=['post'], detail=True, serializer_class=None, filterset_class=None)
    def activation(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        def check_ticket():
            card_set = user.cards.select_related('card').filter(card=instance).first()
            if not card_set:
                raise exceptions.ValidationError({'detail': 'User has not ticket.'})

            ticket = instance.content_object
            if ticket.date_activation:
                raise exceptions.ValidationError({'detail': 'Ticket already activated.'})

            is_enter_ticket = 1 if ticket.type.system_name == 'enter_ticket' else 0
            has_enter_ticket = 1 if user.enter_ticket else 0
            if not has_enter_ticket and is_enter_ticket:
                user.enter_ticket = ticket
                user.save(update_fields=['enter_ticket'])

            currencies = ticket.currencies.select_related('currency').all()
            cards = ticket.cards.select_related('card').all()

            setattr(request, 'coin', dict(
                user=user.auth_id,
                currencies=list()
            ))
            for data in currencies:
                request.coin['currencies'].append({
                    'currency': data.currency.system_name,
                    'amount': data.amount
                })

            for data in cards:
                card = data.card
                amount = data.amount
                if card.content_type.model in ('warriorcard', 'weaponcard', 'armorcard', 'ticket'):
                    if not card.content_object.base:
                        raise exceptions.NotFound('Not found card in store.')

                    object = card.content_object.clone()
                    card = self.get_queryset().get(
                        content_type=object.card.content_type.id,
                        object_id=object.id
                    )
                    CardSet.objects.create(user=user, card=card, count=1)

                elif card in user.get_cards_list():
                    card_set = user.cards.select_related('card').get(card=card)
                    card_set.count += amount
                    card_set.save(update_fields=['count'])
                else:
                    CardSet.objects.create(user=user, card=card, count=amount)

            ticket.date_activation = datetime.now()
            ticket.save(update_fields=['date_activation'])

        client = RpcClient()
        try:
            with transaction.atomic():
                check_ticket()
                client.call('auth', 'accrual', request.coin)
        except exceptions.ValidationError as e: raise e
        except exceptions.APIException as e: raise e
        except Exception as e:
            raise exceptions.APIException(e)

        return Successful()
