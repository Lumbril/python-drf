from rest_framework import status, exceptions, mixins, filters

from django_filters.rest_framework import DjangoFilterBackend

from django.utils.decorators import method_decorator

from apps.api.serializers.guild_serializers import *
from apps.api.serializers.card_serializer import *

from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from django.db.models import OuterRef, Prefetch, Sum

from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema

from apps.api.service import (
    PaginationDefault, PlayerCardTypeFilter,
    CardsFilterBackend, CombatCardFilter,
    UsernameFilter, NotificationFilter
)
from apps.api.serializers import (
    NotificationReadSerializer,
    PotionForWarriorSerializer,
    PlayerShortInfoSerializer,
    BattleResultsSerializer,
    NotificationSerializer,
    PlayerInfoSerializer,
    UserIconSerializer,
    SetupSerializer,
)
from apps.core.models import (
    GuildApplication, GuildRank,
    GuildPlayer
)
from datetime import datetime, timedelta

from packs import Successful, Count


UserModel = get_user_model()


@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(operation_summary="Получение информации о пользователе"))
class PlayerViewSet(mixins.RetrieveModelMixin,
                    GenericViewSet):
    """Информация об игроке"""

    queryset = UserModel.objects.select_related('level').all()
    filter_backends = (CardsFilterBackend,)
    serializer_class = PlayerInfoSerializer
    filterset_class = PlayerCardTypeFilter
    paginator = PaginationDefault()
    search_fields = ('username',)

    def get_queryset(self):
        queryset_guild_player = GuildPlayer.objects.filter(active=True)\
            .select_related('guild')\
            .select_related('rank').all()

        queryset_card_sets = CardSet.objects\
            .select_related('card') \
            .select_related('card__content_type').all()

        queryset_notifications = Notification.objects.filter(
            user=OuterRef('pk'),
            date_reading__isnull=True,
            date_deleted__isnull=True).values('id')

        queryset_applications = GuildApplication.objects.filter(
            whom=OuterRef('pk'),
            type=GuildApplication.Type.INVITATION,
            status=GuildApplication.Status.NEW,
            date_deleted__isnull=True).values('id')

        queryset_main = UserModel.objects.select_related('level')\
            .prefetch_related(Prefetch('guild_player', queryset=queryset_guild_player))\
            .prefetch_related(Prefetch('cards', queryset=queryset_card_sets))\
            .annotate(
                notifications_unread_count=Count(queryset_notifications),
                applications_unread_count=Count(queryset_applications),
                total_power=Sum('cards__card__total_power')).all()
        return queryset_main

    def send_paginated_data(self, request, queryset=queryset, serializer_class=serializer_class):
        page = self.paginator.paginate_queryset(queryset, request)
        serializer = serializer_class(page, many=True)
        return self.paginator.get_paginated_response(data=serializer.data)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        value = self.kwargs[lookup_url_kwarg]
        filter_kwargs = {self.lookup_field: value if int(value) else self.request.user.id}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    @staticmethod
    def sort_by_power(obj):
        return obj.card.content_object.power if hasattr(obj.card.content_object, 'power') else 0

    @swagger_auto_schema(
        operation_summary='Получение списка карт пользователя',
        operation_description='Доступные типы: warriors,weapons,armors,potions,chests'
    )
    @action(methods=['get'], detail=False, url_path='cards', url_name='cards',
            name='get_player_cards', filterset_class=PlayerCardTypeFilter)
    def cards(self, request, *args, **kwargs):
        data = request.user.cards.filter(date_deleted__isnull=True)
        card_set_qs = sorted(self.filter_queryset(data), reverse=True, key=self.sort_by_power)
        return self.send_paginated_data(request, card_set_qs, CardSetSerializer)

    @action(methods=['get'], detail=False, url_path='cards/<int:pk>', url_name='cards',
            name='get_player_cards_retrieve', filterset_class=None, paginator=None)
    def cards_retrieve(self, request, *args, **kwargs):
        card_set = get_object_or_404(request.user.cards.filter(date_deleted__isnull=True), card__pk=kwargs.get('pk'))
        serializer = CardSerializer(card_set.card)

        return Successful(serializer.data)

    @swagger_auto_schema(operation_summary='Получение карт для боя', request_body=SetupSerializer)
    @action(methods=['post'], detail=False, url_path='cards/setup', url_name='setup',
            name='get_player_setup', filterset_class=None, serializer_class=SetupSerializer)
    def setup(self, request, *args, **kwargs):
        serializer = SetupSerializer(data=request.data, user=request.user)
        serializer.is_valid(raise_exception=True)
        if not serializer.data:
            raise exceptions.NotFound('Setup not found.')

        return Successful(serializer.data)

    @action(methods=['get'], detail=False, url_path='cards/potion_types', url_name='potion_types',
            name='get_player_potion_types', filterset_class=CombatCardFilter)
    def potion_types(self, request, *args, **kwargs):
        potion_types = self.filter_queryset(request.user.get_potion_types())
        return self.send_paginated_data(request, potion_types, CardTypeSerializer)

    @action(methods=['get'], detail=False, filterset_class=None,
            serializer_class=ApplicationSerializer)
    @swagger_auto_schema(operation_summary='Получить список приглашений в гильдию')
    def invitation(self, request, *args, **kwargs):
        invitation = GuildApplication.objects.filter(whom=request.user,
                                                     type=GuildApplication.Type.INVITATION,
                                                     status=GuildApplication.Status.NEW)

        return self.send_paginated_data(request, invitation, ApplicationSerializer)

    @invitation.mapping.delete
    @swagger_auto_schema(request_body=ApplicationAcceptSerializer,
                         operation_summary='Отклонить приглашение в гильдию')
    def reject_invitation(self, request, *args, **kwargs):
        invitation = GuildApplication.objects.filter(id=request.data['id'],
                                                     status=GuildApplication.Status.NEW,
                                                     type=GuildApplication.Type.INVITATION)
        if not invitation.exists():
            raise exceptions.NotFound('You don\'t have such an invitation')

        invitation = invitation.first()
        invitation.status = GuildApplication.Status.REJECTED
        invitation.save()

        return Successful()

    @invitation.mapping.put
    @swagger_auto_schema(request_body=ApplicationAcceptSerializer,
                         operation_summary='Принять приглашение в гильдию')
    def accept_invitation(self, request, *args, **kwargs):
        invitation = GuildApplication.objects.filter(
            id=request.data['id'],
            status=GuildApplication.Status.NEW,
            type=GuildApplication.Type.INVITATION,
            date_deleted__isnull=True).first()

        if not invitation:
            raise exceptions.NotFound('You don\'t have such an invitation')

        player = GuildPlayer.objects.filter(player=request.user, active=True).first()

        if player:
            raise exceptions.ValidationError('You are already in the guild')

        rank = GuildRank.objects.filter(name_system='newbie').first()

        if not rank:
            raise exceptions.ValidationError('Admin didn\'t create a *newbie* role')

        invitation = invitation
        guild_player = GuildPlayer()
        guild_player.guild = invitation.to
        guild_player.player = request.user
        guild_player.rank = rank
        guild_player.active = True
        guild_player.save()

        invitation.status = GuildApplication.Status.ACCEPTED
        invitation.save()
        applications = GuildApplication.objects.filter(author=request.user,
                                                       status=GuildApplication.Status.NEW,
                                                       type=GuildApplication.Type.APPLICATION)

        author_rank = GuildPlayer.objects.get(player=invitation.author).rank

        Notification.objects.create_notification(
            user=request.user,
            header='Поздравляю! Вы вступили в гильдию',
            body=f'Приглашение на вступление в гильдию от {invitation.author} {author_rank.name} принято.',
            author=invitation.to.name
        )

        for application in applications:
            application.status = GuildApplication.Status.WITHDRAWN
            application.save()

        return Successful()

    @action(methods=['get'], detail=False, filterset_class=None,
            serializer_class=ApplicationSerializer)
    @swagger_auto_schema(responses={status.HTTP_200_OK: ApplicationSerializer(many=True)},
                         operation_summary='Получить список заявок в гильдию')
    def application(self, request, *args, **kwargs):
        applications = GuildApplication.objects.filter(author=request.user,
                                                       type=GuildApplication.Type.APPLICATION,
                                                       status=GuildApplication.Status.NEW)

        return self.send_paginated_data(request, applications, ApplicationSerializer)

    @application.mapping.delete
    @swagger_auto_schema(request_body=ApplicationAcceptSerializer,
                         operation_summary='Отменить заявку в гильдию')
    def delete_application(self, request, *args, **kwargs):
        application = GuildApplication.objects.filter(author=request.user, id=request.data['id'],
                                                      status=GuildApplication.Status.NEW,
                                                      type=GuildApplication.Type.APPLICATION)
        if not application.exists():
            raise exceptions.NotFound('You don\'t have such an application')

        application = application.first()
        application.status = GuildApplication.Status.WITHDRAWN
        application.save()

        return Successful()

    @action(detail=False, methods=['get'], filter_backends=(DjangoFilterBackend,),
            filterset_class=NotificationFilter)
    @swagger_auto_schema(responses={status.HTTP_200_OK: NotificationSerializer(many=True)},
                         operation_summary='Получение списка уведомлений')
    def notification(self, request, *args, **kwargs):
        notification_qs = Notification.objects.filter(user=request.user, date_deleted__isnull=True)
        notification_qs = self.filter_queryset(notification_qs)

        return self.send_paginated_data(request, notification_qs, NotificationSerializer)

    @notification.mapping.put
    @swagger_auto_schema(request_body=NotificationReadSerializer, operation_summary='Прочитать уведомление')
    def read_notification(self, request, *args, **kwargs):
        notification = Notification.objects.filter(user=request.user, id=request.data['id'], date_deleted__isnull=True,
                                                   date_reading__isnull=True)

        if not notification.exists():
            raise exceptions.ValidationError({'detail': 'there is no such notification or has already been read'})

        notification = notification.first()
        notification.date_reading = datetime.now()
        notification.is_read = True
        notification.save()

        return Successful()

    @action(methods=['get'], detail=False, url_path='info', url_name='get_player_short_info',
            filter_backends=(filters.SearchFilter,), filterset_class=UsernameFilter)
    @swagger_auto_schema(responses={status.HTTP_200_OK: PlayerShortInfoSerializer(many=True)},
                         operation_summary='Получить список краткой информации по пользователям')
    def short_info(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.queryset)
        return self.send_paginated_data(request, queryset, PlayerShortInfoSerializer)

    @swagger_auto_schema(operation_summary='Начисление результатов боя', request_body=BattleResultsSerializer)
    @action(methods=['post'], detail=False, url_path='battle_results', serializer_class=BattleResultsSerializer)
    def battle_results(self, request, *args, **kwargs):
        serializer = BattleResultsSerializer(data=request.data, user=request.user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Successful()

    @action(detail=False, methods=['post'], url_path='potion')
    @swagger_auto_schema(operation_summary='Применить зелье опыта/восстановления', request_body=PotionForWarriorSerializer)
    def use_potion(self, request, *args, **kwargs):
        user = request.user
        potion_id = request.data['potion_id']
        warrior_id = request.data['warrior_id']

        user_card_set = user.cards
        potion_card_set = user_card_set.filter(card_id=potion_id, date_deleted__isnull=True).first()

        if not potion_card_set or potion_card_set.check_is_auction:
            raise exceptions.ValidationError('This potion does not belong to the user or is in the auction')

        potion_card = potion_card_set.card.content_object
        effect = potion_card.specials.all().first()

        if effect.type.system_name not in ['injury_time:decrease', 'card_experience:increase']:
            raise exceptions.ValidationError('A potion with these effects cannot be used')

        warrior_card_set = user_card_set.filter(card_id=warrior_id, date_deleted__isnull=True).first()

        if not warrior_card_set or warrior_card_set.check_is_auction:
            raise exceptions.ValidationError('This warrior does not belong to the user or is in the auction')

        warrior_card = warrior_card_set.card.content_object

        if effect.type.system_name == 'injury_time:decrease':
            if not warrior_card.injured:
                raise exceptions.ValidationError('There is no need to apply this potion.')

            warrior_card.available_from -= timedelta(minutes=effect.value)
        elif effect.type.system_name == 'card_experience:increase':
            warrior_card.experience += effect.value

        potion_card_set.count -= 1

        if potion_card_set.count == 0:
            potion_card_set.date_deleted = datetime.now()

        potion_card_set.save()
        warrior_card.save()

        return Successful()

    @action(detail=False, methods=['put'], url_path='icon')
    @swagger_auto_schema(operation_summary='Обновить иконку у пользователя', request_body=UserIconSerializer)
    def set_icon(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        user.icon = data['icon_url']
        user.save()

        return Successful()
