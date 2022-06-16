from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import mixins, status

from apps.api.service import PaginationDefault

from .serializers import *
from .services import *
from .models import *


@swagger_auto_schema(responses={status.HTTP_200_OK: SystemInfoSerializer})
class SystemInfoViewSet(mixins.ListModelMixin,
                        GenericViewSet):
    """Системная информация"""

    queryset = SystemInfo.objects.select_related('type').select_related('icon').all()
    serializer_class = SystemInfoSerializer
    pagination_class = PaginationDefault
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SystemTypeFilter
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_summary="Получение системной информации")
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        keys = set(i['type'] for i in serializer.data)
        data = {
            key: {
                info['key']: info['value']
                for info in serializer.data
                if info['type'] == key
            }
            for key in keys
        }
        return Response(data)
