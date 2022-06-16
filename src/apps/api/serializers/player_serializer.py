from .guild_serializers import RankSerializer, GuildInfoSerializer

from rest_framework.validators import UniqueValidator

from django.contrib.auth import get_user_model

from apps.core.models import Level, CardSet

from apps.core.models.guild_models import *

from rest_framework import serializers


UserModel = get_user_model()


class PlayerSerializer(serializers.ModelSerializer):

    auth_id = serializers.IntegerField(
        min_value=1,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=UserModel.objects.all()
            )
        ]
    )
    username = serializers.CharField(
        min_length=3,
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=UserModel.objects.all()
            )
        ]
    )

    class Meta:
        model = UserModel
        fields = ('id', 'auth_id', 'username')


class LevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Level
        exclude = ('id',)


class PlayerInfoSerializer(serializers.ModelSerializer):

    icon = serializers.SerializerMethodField()
    level = LevelSerializer(read_only=True)
    guild = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    inv_unread_count = serializers.SerializerMethodField()
    enter_ticket = serializers.SerializerMethodField()
    total_power = serializers.SerializerMethodField()

    def get_icon(self, obj):
        return obj.get_icon()

    def get_total_power(self, obj):
        return obj.total_power if obj.total_power else 0

    def get_guild(self, obj):
        player = obj.guild_player.first()
        if not player:
            return

        serializer = GuildInfoSerializer(
            player.guild, read_only=True).data
        serializer['rank'] = RankSerializer(player.rank).data
        serializer['date_mute'] = player.date_ban

        return serializer

    def get_unread_count(self, obj):
        return obj.notifications_unread_count

    def get_inv_unread_count(self, obj):
        return obj.applications_unread_count

    def get_enter_ticket(self, obj):
        return None if obj.enter_ticket is None else dict(
            name=str(obj.enter_ticket),
            date_activation=obj.enter_ticket.date_activation,
        )

    class Meta:
        depth = 1
        model = UserModel
        fields = ('id', 'username', 'icon', 'level', 'guild', 'personal_exp', 'enter_ticket',
                  'card_exp', 'total_power', 'unread_count', 'inv_unread_count')


class PlayerShortInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = ('id', 'username')


class PotionForWarriorSerializer(serializers.ModelSerializer):

    potion_id = serializers.IntegerField()
    warrior_id = serializers.IntegerField()

    class Meta:
        model = CardSet
        fields = ('potion_id', 'warrior_id')


class UserIconSerializer(serializers.ModelSerializer):

    icon_url = serializers.CharField()

    class Meta:
        model = UserModel
        fields = ('icon_url',)
