from django_filters.rest_framework import DjangoFilterBackend

from django.utils.decorators import method_decorator

from apps.api.service import PaginationDefault

from drf_yasg.utils import swagger_auto_schema

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework import mixins, status

from .serializers import *
from .service import *
from .models import *


@swagger_auto_schema(responses={status.HTTP_200_OK: TranslateSerializer})
class TranslateViewSet(mixins.ListModelMixin,
                       GenericViewSet):
    # TODO: Добавить метод для получения пакета по краткому названию
    """Переводы"""
    queryset = Translate.objects.all()
    serializer_class = TranslateSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TranslateLanguageFilter
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_summary="Получение пакета перевода по коду языка")
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        data = {}
        pack = {}
        data.update({'language': serializer.data[0]['language']})

        for i in serializer.data:
            pack[i['key_translate']] = i['translate']

        data.update({'pack': pack})

        return Response(data)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(operation_summary="Получение списка всех языков"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(operation_summary="Получение информации по языку"))
@swagger_auto_schema(responses={status.HTTP_200_OK: LanguageSerializer(many=True)})
class LanguageViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      GenericViewSet):
    """Языки"""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    pagination_class = PaginationDefault
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (AllowAny,)
