from apps.api.service import PaginationDefault, ChestTypeFilter

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, status, exceptions

from django.utils.decorators import method_decorator

from apps.core.models import Chest, CardSet, Card

from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.api.serializers import (
    OpenChestSerializer, ChestDropSerializer,
    ChestSerializer, DropItemSerializer
)

from django.db import transaction
from django.db.models import F
from datetime import datetime

from packs import Successful
from broker import RpcClient


UserModel = get_user_model()


@method_decorator(name='list',
                  decorator=swagger_auto_schema(operation_summary="Получение информации о сундуках"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(operation_summary="Получение информации о сундуке"))
class ChestViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    queryset = Chest.objects.exclude(date_deleted__lte=datetime.now())
    serializer_class = ChestSerializer
    pagination_class = PaginationDefault
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ChestTypeFilter

    def get_queryset(self):
        queryset = Chest.objects.exclude(date_deleted__lte=datetime.now()) \
            .annotate(card_id=F('card__id')) \
            .select_related('icon') \
            .select_related('currency_purchase') \
            .select_related('currency_sale') \
            .select_related('type__content_type') \
            .select_related('type__icon')

        return queryset

    @swagger_auto_schema(operation_summary='Получить содержимое сундука')
    @action(methods=['get'], detail=True)
    def drop(self, request, *args, **kwargs):
        chest = self.get_object()
        items = chest.items.all()
        serializer = ChestDropSerializer(items, many=True)
        return Successful(serializer.data)

    @swagger_auto_schema(operation_summary='Метод открытия сундука')
    @action(methods=['post'], detail=True, serializer_class=OpenChestSerializer)
    def open(self, request, pk=None):
        chest = get_object_or_404(self.queryset, pk=pk)
        user = request.user
        chest_card = chest.card.all().first()

        if chest_card not in user.get_cards_list():
            return Response({'detail': 'User does not have this chest'}, status=status.HTTP_404_NOT_FOUND)

        drop_items = chest.open()
        drop_items_repr = list()
        for drop in drop_items:
            if drop.card:
                if drop.card.content_type.model == 'warriorcard':
                    if not drop.card.content_object.base:
                        raise exceptions.NotFound('This card isn\'t in the store')
                    object = drop.card.content_object.clone()
                    card = Card.objects.get(
                        content_type=object.card.content_type.id,
                        object_id=object.id
                    )
                    card_set = CardSet(user=user, card=card, count=1)
                    card_set.save()
                elif drop.card in user.get_cards_list():
                    card_set = user.cards.get(card=drop.card)
                    card_set.count += 1
                    card_set.save()
                else:
                    new_card_set = CardSet(user=user, card=drop.card, count=1)
                    new_card_set.save()
            else:
                setattr(request, 'coin', dict(
                    user=request.user.auth_id,
                    currencies=[dict(
                        currency=drop.currency.system_name,
                        amount=drop.amount
                    )]
                ))

                client = RpcClient()
                try:
                    with transaction.atomic():
                        client.call('auth', 'accrual', request.coin)
                except exceptions.ValidationError as e: raise e
                except exceptions.APIException as e: raise e
                except Exception as e:
                    raise exceptions.APIException(e)

            drop_items_repr.append(DropItemSerializer(drop=drop).data)

        chest_set = user.cards.get(card=chest_card)
        chest_set.count -= 1
        chest_set.save()
        user.save()

        return Successful(drop_items_repr)
