from apps.api.serializers import PlayerSerializer, StorageSerializer

from packs.authentication import TokenAuthentication

from apps.api.serializers import (
    SetupSerializer, BattleResultsSerializer,
    PlayerSerializer, BattleLogSerializer,
    CurrencySerializer
)


token_authentication = TokenAuthentication()


def create_player(data):
    serializer = PlayerSerializer(data=data)
    if not serializer.is_valid():
        return dict(
            error=True,
            type='ValidationError',
            message=serializer.errors
        )
    serializer.save()


def create_battle_log(data):
    serializer = BattleLogSerializer(data=data)
    if not serializer.is_valid():
        return dict(
            error=True,
            type='ValidationError',
            message=serializer.errors
        )
    serializer.save()


def create_storage(data):
    serializer = StorageSerializer(data=data)
    if not serializer.is_valid():
        return dict(
            error=True,
            type='ValidationError',
            message=serializer.errors
        )
    serializer.save()


def create_currency(data):
    serializer = CurrencySerializer(data=data)
    if not serializer.is_valid():
        return dict(
            error=True,
            type='ValidationError',
            message=serializer.errors
        )
    serializer.save()

def get_setup(data):
    user, token = token_authentication.authenticate_credentials(data.get('token'))
    if not user:
        return dict(
            error=True,
            type='NotFound',
            message='User not found.'
        )

    serializer = SetupSerializer(data=data, user=user)
    if not serializer.is_valid():
        return dict(
            error=True,
            type='ValidationError',
            message=serializer.errors
        )

    if not serializer.data:
        return dict(
            error=True,
            type='ValidationError',
            message=''
        )
    return serializer.data


def charge_battle_results(data):
    user, token = token_authentication.authenticate_credentials(data.get('token'))
    if not user:
        return dict(
            error=True,
            type='NotFound',
            message='User not found.'
        )

    serializer = BattleResultsSerializer(data=data, user=user)
    if not serializer.is_valid():
        return dict(
            error=True,
            type='ValidationError',
            message=serializer.errors
        )
    serializer.save()
