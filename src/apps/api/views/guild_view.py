from apps.api.service import PaginationDefault, GuildOpenFilter

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, status, exceptions

from django.utils.decorators import method_decorator

from apps.api.serializers.guild_serializers import *

from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.core.models.guild_models import *
from apps.core.models import Notification

from datetime import datetime, timedelta

from django.db.models import Sum, Q

from packs import Successful


UserModel = get_user_model()


@method_decorator(name='list',
                  decorator=swagger_auto_schema(operation_summary="Получение информации о гильдиях"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(operation_summary="Получение информации о гильдии"))
class GuildViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    """Информация о гильдии"""

    filter_backends = (DjangoFilterBackend, SearchFilter)
    permission_classes = [IsAuthenticated]
    pagination_class = PaginationDefault
    serializer_class = GuildSerializer
    filterset_class = GuildOpenFilter
    queryset = Guild.objects.exclude(date_deleted__lte=datetime.now())
    search_fields = ('name',)

    def get_queryset(self):
        queryset = Guild.objects.select_related('location')\
            .exclude(date_deleted__lte=datetime.now())\
            .annotate(total_power=Sum('players__player__cards__card__total_power', filter=Q(players__active=True)))
        return queryset

    def send_paginated_data(self, request, queryset=None, serializer_class=None):
        serializer_class = serializer_class if serializer_class is not None else self.serializer_class
        queryset = queryset if queryset is not None else self.queryset
        page = self.paginator.paginate_queryset(queryset, request)
        serializer = serializer_class(page, many=True)

        return self.paginator.get_paginated_response(data=serializer.data)

    @swagger_auto_schema(request_body=GuildCreateSerializer, operation_summary='Создание гильдии')
    def create(self, request):
        if GuildPlayer.objects.filter(player=request.user.id, active=True).exists():
            raise exceptions.ValidationError({'detail': 'Player already in the guild'})

        leader_rank = GuildRank.objects.filter(name_system='leader')
        if not leader_rank.exists():
            leader_rank = GuildRank.objects.create(
                opportunity_accept_application=True,
                name_system='leader',
                name='Лидер',
                worth=0
            )
        else:
            leader_rank = leader_rank.first()

        serializer = GuildCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        guild = serializer.save()
        guild.save()

        GuildPlayer.objects.create(
            player=request.user,
            rank=leader_rank,
            guild=guild,
        )
        return Successful(serializer.data)

    @action(detail=False, methods=['put'], url_path='info')
    @swagger_auto_schema(request_body=GuildCreateSerializer, operation_summary='Обновление информации гильдии')
    def update_info(self, request):
        # TODO: разобраться с обновлением через сериализатор
        guild_player = GuildPlayer.objects.filter(player=request.user.id, active=True)
        if not guild_player.exists():
            raise exceptions.ValidationError({'detail': 'Player already in the guild'})

        guild_player = guild_player.first()
        if guild_player.rank.name_system != 'leader':
            raise exceptions.ValidationError({'detail': 'Player hasn\'t rights'})

        data = request.data
        guild = Guild.objects.filter(id=guild_player.guild.id, date_deleted__isnull=True)
        if not guild.exists():
            raise exceptions.ValidationError({'detail': 'Guild doesn\'t exist'})

        guild = guild.first()
        location = Country.objects.get(
            id=data.get('location', guild.location.id)
        ) if data.get('location', 0) != 0 else guild.location
        guild.name = data.get('name', guild.name)
        guild.description = data.get('description', guild.description)
        guild.icon = data.get('icon', guild.icon)
        guild.type = data.get('type', guild.type)
        guild.location = location
        guild.threshold = data.get('threshold', guild.threshold)
        guild.save()

        return Successful()

    @action(detail=False, methods=['delete'], name='leave guild')
    @swagger_auto_schema(request_body=VoidSerializer, operation_summary='Покинуть гильдию')
    def leave(self, request):
        user = request.user

        player = GuildPlayer.objects.filter(player=user, active=True)

        if not player.exists():
            return Response({'Player isn\'t in this guild'}, status=status.HTTP_400_BAD_REQUEST)

        player = player.first()

        if player.rank.name_system == "leader":
            return Response({'Leader can\'t leave the guild'}, status=status.HTTP_400_BAD_REQUEST)

        player.active = False
        player.save()

        return Successful()

    @action(detail=False, methods=['delete'], name='kick from guild')
    @swagger_auto_schema(request_body=KickUserSerializer, operation_summary='Исключить игрока')
    def kick(self, request):
        user = request.user
        data = request.data

        guild_leader = GuildPlayer.objects.filter(player_id=user.id, active=True).first()
        player_kick = GuildPlayer.objects.filter(player_id=data['id'], active=True).first()

        if not guild_leader:
            raise exceptions.ValidationError('You are not in the guild')

        if not player_kick:
            raise exceptions.ValidationError('The player who is expelled is not in the guild')

        if not (guild_leader.guild.tag == player_kick.guild.tag):
            raise exceptions.ValidationError('You are from different guilds')

        if guild_leader.rank.worth >= player_kick.rank.worth:
            raise exceptions.ValidationError("You don't have sufficient rights for this action.")

        player_kick.active = False
        player_kick.save()

        guild_name = guild_leader.guild.name
        Notification.objects.create_notification(
            user=player_kick.player,
            header=f'Вас исключили из гильдии {guild_name}',
            body=f'Игрок {guild_leader.rank.name} {guild_leader.player.username} исключил вас из гильдии {guild_name}',
            author=guild_name
        )

        return Successful()

    @action(detail=False, methods=['delete'], url_path='status')
    @swagger_auto_schema(request_body=VoidSerializer, operation_summary='Удалить гильдию')
    def delete_guild(self, request):
        guild_player = GuildPlayer.objects.filter(player=request.user.id, active=True)

        if not guild_player.exists():
            return Response({'Player isn\'t in guild'}, status=status.HTTP_400_BAD_REQUEST)

        obj = guild_player.first()
        guild = obj.guild

        if obj.rank.name_system != 'leader':
            return Response({'data': 'Player hasn\'t rights'}, status=status.HTTP_400_BAD_REQUEST)

        guild_players = GuildPlayer.objects.filter(guild=guild, active=True)

        for player in guild_players:
            player.active = False
            player.save()

        guild_applications = GuildApplication.objects.filter(to=guild, status=GuildApplication.Status.NEW,
                                                             type=GuildApplication.Type.APPLICATION)

        for application in guild_applications:
            application.status = GuildApplication.Status.WITHDRAWN
            application.date_edited = datetime.now()
            application.date_deleted = datetime.now()
            application.save()

        guild.date_deleted = datetime.now()
        guild.save()

        return Successful()

    @action(detail=False, methods=['get'], name='get all ranks of guild',
            url_path='rank', filterset_class=None, filter_backends=())
    @swagger_auto_schema(responses={status.HTTP_200_OK: RankSerializer(many=True)},
                         operation_summary='Получить список всех доступных званий')
    def rank(self, request):
        ranks = GuildRank.objects.all()
        serializer = RankSerializer(ranks, many=True)

        return Successful(serializer.data)

    @rank.mapping.put
    @swagger_auto_schema(request_body=NewRankSerializer, operation_summary='Изменить звание')
    def rank_update(self, request):
        user = request.user
        data = request.data

        if user.id == data['player_id']:
            return Response({"You can't change your own rank"}, status=status.HTTP_400_BAD_REQUEST)

        player_who = GuildPlayer.objects.filter(player_id=user.id, active=True).first()
        player_whom = GuildPlayer.objects.filter(player_id=data['player_id'], active=True).first()

        if not player_who:
            return exceptions.ValidationError("Player isn't in guild")

        if not player_whom:
            return exceptions.ValidationError("The player who is re-ranked isn't in the guild")

        if not (player_who.guild.tag == player_whom.guild.tag):
            return exceptions.ValidationError('You are from different guilds')

        old_rank = player_whom.rank
        new_rank = GuildRank.objects.filter(id=data['rank']).first()

        if not new_rank:
            return exceptions.ValidationError('This rank does not exist')

        if player_who.rank.worth >= new_rank.worth:
            return exceptions.ValidationError("You don't have sufficient rights to do this.")

        player_whom.rank = new_rank
        player_whom.save()

        guild_name = player_who.guild.name
        Notification.objects.create_notification(
            user=player_whom.player,
            header=f'Ваш ранг в гильдии {guild_name} изменен',
            body=f'Игрок {player_who.rank.name} {player_who.player.username} изменил ваш ранг в гильдии {guild_name} '
                 f'с {old_rank.name} на {new_rank.name}',
            author=guild_name
        )

        return Successful()

    @action(detail=False, methods=['put'], name='mute')
    @swagger_auto_schema(request_body=KickUserSerializer, operation_summary='Дать бан на час в чате')
    def mute(self, request):
        user = request.user
        data = request.data

        leader = GuildPlayer.objects.filter(player_id=user.id, active=True).first()
        player = GuildPlayer.objects.filter(player_id=data['id'], active=True).first()

        if not leader:
            raise exceptions.ValidationError("Player isn't in guild")

        if not player:
            raise exceptions.ValidationError("The player who is given a ban in the chat isn't in the guild")

        if not (leader.guild.tag == player.guild.tag):
            raise exceptions.ValidationError('You are from different guilds')

        if leader.rank.worth >= player.rank.worth:
            raise exceptions.ValidationError("You don't have sufficient rights for this action.")

        player.date_ban = datetime.now() + timedelta(hours=1)
        player.save()

        guild_name = player.guild.name
        Notification.objects.create_notification(
            user=player.player,
            header=f'Вам запретили писать в чат в гильдии {guild_name}',
            body=f'Игрок {leader.rank.name} {leader.player.username} запретил вам писать в чате гилдии {guild_name} '
                 f'до {player.date_ban}',
            author=guild_name
        )

        return Successful()

    @action(detail=False, methods=['get'], name='get application in guild',
            url_path='application', filterset_class=None, filter_backends=())
    @swagger_auto_schema(responses={status.HTTP_200_OK: ApplicationSerializer(many=True)},
                         operation_summary='Получить список заявок в гильдию')
    def application(self, request):
        guild_player = GuildPlayer.objects.filter(player=request.user, active=True)

        if not guild_player.exists():
            return Response({'You are not a member of this guild'}, status=status.HTTP_400_BAD_REQUEST)

        guild = guild_player.first().guild

        guild_applications = GuildApplication.objects.filter(to=guild, status=GuildApplication.Status.NEW,
                                                             type=GuildApplication.Type.APPLICATION)

        return self.send_paginated_data(request, guild_applications, ApplicationSerializer)

    @application.mapping.post
    @swagger_auto_schema(request_body=EnterGuildSerializer,
                         operation_summary='Оставить заявку на вступление в открытую гильдию')
    def create_application(self, request):
        data = request.data
        user = request.user

        player_guild = GuildPlayer.objects.filter(player=user, active=True).first()

        if player_guild:
            raise exceptions.ValidationError('You are already in the guild')

        guild = Guild.objects.filter(id=data['id'], date_deleted__isnull=True).first()

        if not guild:
            raise exceptions.ValidationError('There is no such guild')

        if not guild.type:
            raise exceptions.ValidationError('Guild closed')

        another_guild_application = GuildApplication.objects\
            .filter(author=user, status=GuildApplication.Status.NEW).first()

        if another_guild_application:
            another_guild_application.date_deleted = datetime.now()
            another_guild_application.save()

        application = GuildApplication()
        application.type = GuildApplication.Type.APPLICATION
        application.status = GuildApplication.Status.NEW
        application.author = user
        application.whom = user
        application.to = guild
        application.save()

        return Successful()

    @application.mapping.delete
    @swagger_auto_schema(request_body=ApplicationAcceptSerializer, operation_summary='Отклонить заявку')
    def reject_application(self, request):
        data = request.data
        user = request.user

        guild_player = GuildPlayer.objects.filter(player=user, active=True)

        if not guild_player.exists():
            return Response({'You are not a member of this guild'}, status=status.HTTP_400_BAD_REQUEST)

        guild_player = guild_player.first()
        guild = guild_player.guild
        application = GuildApplication.objects.filter(id=data['id'], to=guild, status=GuildApplication.Status.NEW,
                                                      type=GuildApplication.Type.APPLICATION)
        if not guild_player.rank.opportunity_accept_application:
            return Response({'You don\'t have that opportunity'}, status=status.HTTP_400_BAD_REQUEST)

        if not application.exists():
            return Response({'There is no such application to the guild'}, status=status.HTTP_400_BAD_REQUEST)

        application = application.first()
        application.status = GuildApplication.Status.REJECTED
        application.date_change = datetime.now()
        application.save()

        return Successful()

    @application.mapping.put
    @swagger_auto_schema(request_body=ApplicationAcceptSerializer, operation_summary='Принять заявку')
    def accept_application(self, request):
        data = request.data
        user = request.user

        guild_player = GuildPlayer.objects.filter(player=user, active=True)

        if not guild_player.exists():
            return Response({'You are not a member of this guild'}, status=status.HTTP_400_BAD_REQUEST)

        guild_player = guild_player.first()
        guild = guild_player.guild
        application = GuildApplication.objects.filter(id=data['id'], to=guild, status=GuildApplication.Status.NEW,
                                                      type=GuildApplication.Type.APPLICATION)

        if not application.exists():
            return Response({'There is no such application to the guild'}, status=status.HTTP_400_BAD_REQUEST)

        if not guild_player.rank.opportunity_accept_application:
            return Response({'You don\'t have that opportunity'}, status=status.HTTP_400_BAD_REQUEST)

        application = application.first()
        player = GuildPlayer.objects.filter(player=application.whom, active=True)

        if player.exists():
            return Response({'The player is already a member of the guild'}, status=status.HTTP_400_BAD_REQUEST)

        rank = GuildRank.objects.filter(name_system='newbie')

        if not rank.exists():
            new_rank = GuildRank()
            new_rank.name = 'Новичок'
            new_rank.name_system = 'newbie'
            new_rank.worth = 10
            new_rank.opportunity_accept_application = False
            new_rank.save()
            rank = new_rank
        else:
            rank = rank.first()

        new_player = GuildPlayer()
        new_player.guild = application.to
        new_player.player = application.whom
        new_player.rank = rank
        new_player.active = True
        new_player.save()

        application.status = GuildApplication.Status.ACCEPTED
        application.date_change = datetime.now()
        application.save()

        Notification.objects.create_notification(
            user=request.user,
            header='Поздравляю! Вы вступили в гильдию',
            body=f'Запрос на вступление в гильдию принят {application.author} {guild_player.rank.name}',
            author=application.to.name
        )

        return Successful()

    @action(detail=False, methods=['get'], name='get list invitation',
            url_path='invitation', filterset_class=None, filter_backends=())
    @swagger_auto_schema(responses={status.HTTP_200_OK: ApplicationSerializer(many=True)},
                         operation_summary='Получить список приглашений, созданных гильдией')
    def invitation(self, request):
        guild_player = GuildPlayer.objects.filter(player=request.user, active=True)

        if not guild_player.exists():
            return Response({'You are not a member of this guild'}, status=status.HTTP_400_BAD_REQUEST)

        guild = guild_player.first().guild

        guild_applications = GuildApplication.objects.filter(to=guild, status=GuildApplication.Status.NEW,
                                                             type=GuildApplication.Type.INVITATION)

        return self.send_paginated_data(request, guild_applications, ApplicationSerializer)

    @invitation.mapping.post
    @swagger_auto_schema(request_body=InvitationCreateSerializer, operation_summary='Создать приглашение')
    def create_invitation(self, request):
        data = request.data
        user = request.user

        if user.id == data['player_id']:
            raise exceptions.ValidationError("You cannot invite yourself to the guild")

        guild_player = GuildPlayer.objects.filter(player=user, active=True).first()

        if not guild_player:
            raise exceptions.ValidationError("You are not a member of a guild")

        if guild_player.rank.name_system != 'leader':
            raise exceptions.ValidationError("Only the leader can send invitations to the guild")

        invent_player = GuildPlayer.objects.filter(player_id=data['player_id'], active=True).first()

        if invent_player and guild_player.guild_id == invent_player.guild_id:
            raise exceptions.ValidationError("You can not invite members of your guild")

        invent_player = UserModel.objects.filter(id=data['player_id']).first()

        if not invent_player:
            raise exceptions.ValidationError("The player doesn't exist")

        invitation_to_player = GuildApplication.objects.filter(
            whom=invent_player,
            status=GuildApplication.Status.NEW,
            to=guild_player.guild,
            date_deleted__isnull=True)

        if invitation_to_player:
            raise exceptions.ValidationError('You have already invited this player')

        guild = guild_player.guild

        invitation = GuildApplication()
        invitation.type = GuildApplication.Type.INVITATION
        invitation.status = GuildApplication.Status.NEW
        invitation.to = guild
        invitation.author = guild_player.player
        invitation.whom = invent_player
        invitation.save()

        return Successful()

    @invitation.mapping.delete
    @swagger_auto_schema(request_body=ApplicationAcceptSerializer, operation_summary='Удалить приглашение')
    def delete_invitation(self, request):
        data = request.data
        user = request.user

        guild_player = GuildPlayer.objects.filter(player=user, active=True)

        if not guild_player.exists():
            return Response({'You are not a member of this guild'}, status=status.HTTP_400_BAD_REQUEST)

        guild_player = guild_player.first()
        guild = guild_player.guild
        invitation = GuildApplication.objects.filter(id=data['id'], to=guild, type=GuildApplication.Type.INVITATION,
                                                     status=GuildApplication.Status.NEW)

        if not guild_player.rank.opportunity_accept_application:
            return Response({'You don\'t have that opportunity'}, status=status.HTTP_400_BAD_REQUEST)

        if not invitation.exists():
            return Response({'The guild didn\'t create such an invitation'}, status=status.HTTP_400_BAD_REQUEST)

        invitation = invitation.first()
        invitation.status = GuildApplication.Status.REJECTED
        invitation.date_change = datetime.now()
        invitation.save()

        return Successful()

    @action(detail=False, methods=['get'], name='get list countries',
            url_path='locations', filterset_class=None, filter_backends=())
    @swagger_auto_schema(responses={status.HTTP_200_OK: CountrySerializer}, operation_summary='Получить список стран')
    def get_countries(self, request):
        queryset = Country.objects.all()
        serializer = CountrySerializer(queryset, many=True)

        return Successful(serializer.data)
