from django.contrib.auth import get_user_model

from apps.core.models.guild_models import *

from rest_framework import serializers

from django.db.models import Sum


UserModel = get_user_model()


class RankSerializer(serializers.ModelSerializer):

    class Meta:
        model = GuildRank
        fields = '__all__'


class PlayersGuildSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {
            'id': obj.player.id,
            'name': obj.player.username,
            'icon': obj.player.get_icon(),
            'total_power': obj.total_power if obj.total_power else 0
        }

    def get_rank(self, obj):
        return RankSerializer(obj.rank).data

    class Meta:
        model = GuildPlayer
        exclude = ('id', 'guild', 'player')


class GuildSerializer(serializers.ModelSerializer):

    icon = serializers.SerializerMethodField()
    players_guild = serializers.SerializerMethodField()
    total_power = serializers.SerializerMethodField()

    def get_total_power(self, guild):
        return guild.total_power if guild.total_power else 0

    def get_icon(self, obj):
        return obj.get_icon()

    def get_players_guild(self, guild):
        player_guild_qs = GuildPlayer.objects\
            .select_related('guild', 'player', 'rank')\
            .prefetch_related('player__cards')\
            .filter(guild=guild, active=True)\
            .annotate(total_power=Sum('player__cards__card__total_power'))
        return PlayersGuildSerializer(player_guild_qs, many=True).data

    class Meta:
        depth = 1
        model = Guild
        exclude = ('date_created', 'date_edited', 'date_deleted')


class GuildInfoSerializer(serializers.ModelSerializer):

    icon = serializers.SerializerMethodField()

    def get_icon(self, obj):
        return obj.get_icon()

    class Meta:
        model = Guild
        fields = ('id', 'name', 'icon')


class GuildCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return Guild(**validated_data)

    def update(self, instance, validated_data):
        instance.name_system = validated_data.get('name', instance.name_system)
        instance.description = validated_data.get('description', instance.description)
        instance.icon = validated_data.get('icon', instance.icon)
        instance.type = validated_data.get('type', instance.type)
        instance.location = validated_data.get('location', instance.location)
        instance.threshold = validated_data.get('threshold', instance.threshold)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['icon'] = instance.get_icon()
        return representation

    class Meta:
        model = Guild
        exclude = ('max_count_players', 'tag', 'date_created', 'date_deleted')


class VoidSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = []


class KickUserSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()

    class Meta:
        model = UserModel
        fields = ('id',)


class NewRankSerializer(serializers.ModelSerializer):

    player_id = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all())
    rank = serializers.PrimaryKeyRelatedField(queryset=GuildRank.objects.all())

    class Meta:
        model = GuildPlayer
        fields = ('player_id', 'rank')


class RankSerializer(serializers.ModelSerializer):

    class Meta:
        model = GuildRank
        fields = '__all__'


class EnterGuildSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()

    class Meta:
        model = Guild
        fields = ('id',)


class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = ('id', 'username', 'icon')


class ApplicationSerializer(serializers.ModelSerializer):

    to = serializers.SerializerMethodField()
    author = UserInfoSerializer(read_only=True)
    whom = UserInfoSerializer(read_only=True)

    def get_to(self, guild):
        to_qs = Guild.objects.get(id=guild.to.id)
        return GuildInfoSerializer(to_qs).data

    class Meta:
        model = GuildApplication
        exclude = ('date_edited', 'date_deleted')


class ApplicationAcceptSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()

    class Meta:
        model = GuildApplication
        fields = ('id',)


class InvitationCreateSerializer(serializers.ModelSerializer):

    player_id = serializers.IntegerField()

    class Meta:
        model = GuildApplication
        fields = ('player_id',)


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ('id', 'country')
