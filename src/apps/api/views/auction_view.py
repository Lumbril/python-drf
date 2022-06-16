from django_filters.rest_framework import DjangoFilterBackend

from django.utils.decorators import method_decorator

from drf_yasg.utils import swagger_auto_schema

from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework import mixins, exceptions

from apps.api.service import (
    PaginationDefault, AuctionFilter
)
from apps.api.serializers import (
    AuctionLotPurchaseSerializer,
    AuctionLotCreateSerializer,
    AuctionLotSerializer,
)
from apps.core.models import (
    CardSet, Currency, AuctionLot
)
from django.db import transaction

from datetime import datetime

from broker import RpcClient
from packs import (
    IsEnoughBalance,
    Successful
)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение списка лотов"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(
                      operation_summary="Получение информации о лоте"))
class AuctionLotView(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    """Список аукционных лотов\n
    Доступные типы: warriorcard,weaponcard,armorcard,potioncard,chest"""

    queryset = AuctionLot.objects.filter(date_deleted__isnull=True)
    serializer_class = AuctionLotSerializer
    pagination_class = PaginationDefault
    filterset_class = AuctionFilter
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        queryset = AuctionLot.objects.filter(date_deleted__isnull=True)\
            .select_related('user', 'lot', 'currency', 'lot__card', 'lot__card__content_type')
        return queryset

    def send_paginated_data(self, request, queryset=None, serializer_class=None):
        serializer_class = serializer_class if serializer_class is not None else self.serializer_class
        queryset = queryset if queryset is not None else self.get_queryset()
        page = self.paginator.paginate_queryset(queryset, request)
        serializer = serializer_class(page, many=True)

        return self.paginator.get_paginated_response(data=serializer.data)
    
    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.filter_queryset(self.get_queryset())

        pagination_data = self.send_paginated_data(request, queryset)

        for i in range(len(pagination_data.data['results'])):
            user_id = pagination_data.data['results'][i]['user']

            if user_id:
                pagination_data.data['results'][i]['is_my'] = True if user_id['id'] == user.id \
                                                                else False
            else:
                pagination_data.data['results'][i]['is_my'] = False

        return pagination_data

    @swagger_auto_schema(request_body=AuctionLotCreateSerializer, operation_summary='Создать лот')
    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        lot = CardSet.objects.filter(card_id=data['card_id'], user=user,
                                     date_deleted__isnull=True).first()
        if not lot or lot.check_is_auction:
            raise exceptions.ValidationError('You do not have such a card or it is already on the auction')

        currency = Currency.objects.filter(system_name=data['currency_name']).first()
        if not currency:
            raise exceptions.ValidationError('There is not such currency')

        if data['cost'] < 0:
            raise exceptions.ValidationError('The cost can not be negative')

        if not (lot.card.content_type.model in ['warriorcard', 'weaponcard', 'armorcard']):
            new_lot = CardSet()
            new_lot.user = user
            new_lot.card = lot.card
            new_lot.count = 1
            new_lot.save()
            lot.count -= 1

            if lot.count == 0:
                lot.count = 1
                lot.date_deleted = datetime.now()

            lot.save()
            lot = new_lot

        lot.save()
        auction = AuctionLot()
        auction.lot = lot
        auction.user = user
        auction.currency = currency
        auction.cost = data['cost']
        auction.save()

        return Successful()

    @swagger_auto_schema(operation_summary='Отозвать лот')
    def destroy(self, request, *args, **kwargs):
        user = request.user
        auction_lot = AuctionLot.objects.filter(id=self.kwargs.get('pk'),
                                                lot__user=user,
                                                date_deleted__isnull=True).first()

        if not auction_lot:
            raise exceptions.ValidationError('There is not such lot')

        check = False

        if not (auction_lot.lot.card.content_type.model in ['warriorcard', 'weaponcard', 'armorcard']):
            if auction_lot.lot.card in user.get_cards_no_auction():
                check = True
                card_set = user.cards.filter(card=auction_lot.lot.card, date_deleted__isnull=True)

                for i in card_set:
                    if i.check_is_auction:
                        card_set = card_set.exclude(pk=i.id)

                card_set.count += 1
                card_set.save()

        auction_lot.date_deleted = datetime.now()

        card_set = auction_lot.lot

        if not (card_set.card.content_type.model in ['warriorcard', 'weaponcard', 'armorcard']) \
                and check:
            card_set.date_deleted = datetime.now()

        card_set.save()
        auction_lot.save()

        return Successful()

    @action(detail=True, methods=['post'], serializer_class=AuctionLotPurchaseSerializer,
            permission_classes=[IsEnoughBalance])
    @swagger_auto_schema(operation_summary='Купить лот')
    def purchase(self, request, *args, **kwargs):
        user = request.user
        auction_lot = self.get_object()

        def confirm_lot():
            if auction_lot.lot.user == user:
                raise exceptions.ValidationError('You can not buy a card from yourself')

            card_set = auction_lot.lot
            check = False

            if not (card_set.card.content_type.model in ['warriorcard', 'weaponcard', 'armorcard']):
                if card_set.card in user.get_cards_no_auction():
                    check = True
                    card = user.cards.get(card=auction_lot.lot.card, date_deleted__isnull=True)

                    for i in card:
                        if i.check_is_auction:
                            card = card.exclude(id=i.id)

                    card.count += 1
                    card.save()

            auction_lot.date_deleted = datetime.now()

            if not (card_set.card.content_type.model in ['warriorcard', 'weaponcard', 'armorcard']) \
                    and check:
                card_set.date_deleted = datetime.now()

            old_user = card_set.user
            card_set.user = user

            card_set.save()
            auction_lot.save()

            setattr(request, 'coin', dict(
                user=old_user.auth_id,
                currencies=[dict(
                    currency=auction_lot.currency.system_name,
                    amount=auction_lot.cost
                )]
            ))

        try:
            with transaction.atomic():
                confirm_lot()
                client = RpcClient()
                client.call('auth', 'withdrawal', request.cost)
                client = RpcClient()
                client.call('auth', 'accrual', request.coin)
        except exceptions.ValidationError as e: raise e
        except exceptions.APIException as e: raise e
        except Exception as e:
            raise exceptions.APIException(e)

        return Successful()
