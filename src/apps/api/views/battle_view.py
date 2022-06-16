from apps.api.serializers import BattleLogSerializer

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from apps.battle.models import *


class BattleLogViewSet(mixins.CreateModelMixin,
                       GenericViewSet):

    queryset = BattleLog.objects.all()
    serializer_class = BattleLogSerializer
