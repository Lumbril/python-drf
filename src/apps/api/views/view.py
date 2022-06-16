from django_filters.rest_framework import DjangoFilterBackend

from django.utils.decorators import method_decorator

from rest_framework.viewsets import GenericViewSet

from apps.core.models import Level, GuildPlayer

from drf_yasg.utils import swagger_auto_schema

from apps.api.service import PaginationDefault
from apps.api.serializers import (
    ChatLogSerializer, LevelSerializer
)

from django.db.models import Prefetch

from apps.chat.models import ChatLog

from rest_framework import mixins


@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(operation_summary="Получение информации по уровню"))
@method_decorator(name='list',
                  decorator=swagger_auto_schema(operation_summary="Получение таблицы уровней"))
class LevelViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericViewSet):
    """Информация по системе уровней"""

    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    pagination_class = PaginationDefault
    filter_backends = (DjangoFilterBackend,)


class ChatLogViewSet(mixins.RetrieveModelMixin,
                     GenericViewSet):
    """Логи чата"""

    queryset = ChatLog.objects.all()
    serializer_class = ChatLogSerializer
    pagination_class = PaginationDefault

    def get_queryset(self):
        guild_players = GuildPlayer.objects.select_related('rank', 'player', 'guild')
        queryset = ChatLog.objects.select_related('user', 'guild', 'guild__location')\
            .prefetch_related(Prefetch('user__guild_player', queryset=guild_players))
        return queryset

    @swagger_auto_schema(operation_summary="Логи чата по id гильдии")
    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(guild__id=kwargs['pk']).order_by('-time')
        page = self.paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(page, many=True)
        return self.paginator.get_paginated_response(data=serializer.data)
