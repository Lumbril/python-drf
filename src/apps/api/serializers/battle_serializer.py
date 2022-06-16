from rest_framework import serializers, exceptions

from django.contrib.auth import get_user_model

from apps.core.models.card_models import *

from datetime import datetime, timedelta

from .mixins import PowerSerializerMixin

from apps.battle.models import *

from .card_serializer import (
    WarriorCardSerializer,
    PotionCardSerializer,
    WeaponCardSerializer,
    ArmorCardSerializer
)
from broker import RpcClient


UserModel = get_user_model()


class BattleRoundSerializer(serializers.ModelSerializer):

    class Meta:
        model = BattleRound
        fields = ('data',)


class BattleLogSerializer(serializers.ModelSerializer):

    rounds = BattleRoundSerializer(many=True, required=False)

    def create(self, validated_data):
        rounds = validated_data.pop('rounds')
        battle = BattleLog.objects.create(**validated_data)
        for round in rounds:
            round = dict(round)
            BattleRound.objects.create(battle=battle, data=round['data'])
        return battle

    class Meta:
        model = BattleLog
        fields = '__all__'


class UserSetupInfoSerializer(serializers.ModelSerializer, PowerSerializerMixin):

    icon = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    guild = serializers.SerializerMethodField()

    def get_icon(self, obj):
        return obj.get_icon()

    def get_level(self, obj):
        return obj.level.level if obj.level and obj.level.level else 1
    
    def get_guild(self, obj):
        player = obj.guild_player.first()
        if not player:
            return None

        return player.guild.name

    class Meta:
        model = UserModel
        fields = ('id', 'username', 'icon', 'guild', 'total_power', 'level')


class Bet(serializers.Serializer):

    currency = serializers.CharField()
    amount = serializers.FloatField()


class SetupSerializer(serializers.Serializer):

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.cards_qs = self.user.cards.all() if self.user else None

    warrior_card_id = serializers.IntegerField(min_value=1)
    weapon_card_id = serializers.IntegerField(min_value=1)
    armor_card_id = serializers.IntegerField(min_value=1)
    potion_card_types_id = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        max_length=6
    )
    bet = Bet()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        setup = dict()
        if not self.cards_qs:
            return setup

        client = RpcClient()
        try:
            balance = client.call('auth', 'get_balance', {
                'key': self.user.auth_token.key
            }).get('balance',)
        except exceptions.PermissionDenied as e: raise e
        except exceptions.ValidationError as e:
            raise exceptions.AuthenticationFailed(e.detail)
        except Exception as e:
            raise exceptions.AuthenticationFailed(e)

        bet = data.get('bet')
        for balance_obj in balance:
            if balance_obj.get('system_name') == bet.get('currency') \
                    and balance_obj.get('amount') >= bet.get('amount'):
                break
        else:
            raise exceptions.ValidationError('Invalid bet')

        warriors = self.cards_qs.filter(
            card__content_type__model=WarriorCard.__name__.lower())
        weapons = self.cards_qs.filter(
            card__content_type__model=WeaponCard.__name__.lower())
        armors = self.cards_qs.filter(
            card__content_type__model=ArmorCard.__name__.lower())
        potions = self.cards_qs.filter(
            card__content_type__model=PotionCard.__name__.lower())
        warrior = warriors.filter(
            card__pk=data.get('warrior_card_id',)).first()
        weapon = weapons.filter(card__pk=data.get('weapon_card_id',)).first()
        armor = armors.filter(card__pk=data.get('armor_card_id',)).first()

        if not (warrior and weapon and armor):
            return setup

        if warrior.card.content_object.injured:
            return setup

        potions_list = list()
        for type_id in data.get('potion_card_types_id',):
            one_type_potions = list()
            for potion in potions:
                if potion.card.content_object.type.id == type_id:
                    potion_data = PotionCardSerializer(
                        potion.card.content_object).data
                    potion_data['card_count'] = potion.count
                    one_type_potions.append(potion_data)

            if one_type_potions:
                potions_list.append(one_type_potions)

        setup['warrior'] = WarriorCardSerializer(
            warrior.card.content_object).data
        setup['weapon'] = WeaponCardSerializer(weapon.card.content_object).data
        setup['armor'] = ArmorCardSerializer(armor.card.content_object).data
        setup['potions'] = potions_list
        setup['user'] = UserSetupInfoSerializer(self.user).data
        return setup


class BattleResultsSerializer(serializers.Serializer):

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    BATTLE_RESULTS = (
        (-1, 'defeat'),
        (0, 'draw'),
        (1, 'victory')
    )

    battle_result = serializers.ChoiceField(choices=BATTLE_RESULTS)
    warrior_card_id = serializers.IntegerField(min_value=1)
    card_exp = serializers.FloatField(min_value=0)
    user_exp = serializers.FloatField(min_value=0)
    warrior_exp = serializers.FloatField(min_value=0)
    injury_time = serializers.TimeField(default='00:00:00')
    progress = serializers.FloatField(min_value=0)
    used_potions = serializers.ListField(
        child=serializers.ListField(
            child=serializers.IntegerField(min_value=1),
            max_length=2, min_length=2)
    )
    bet = Bet()

    def save(self):
        if not self.user:
            return None

        data = self.validated_data
        self.user.card_exp += data.get('card_exp')
        self.user.personal_exp += data.get('user_exp')
        self.user.save()

        currency, amount = data.get('bet').values()
        accrual = True if amount > 0 else False
        body = dict(
            user=self.user.auth_id,
            currencies=[dict(
                currency=currency,
                amount=abs(amount)
            )]
        )

        client = RpcClient()
        if abs(amount) >= 1:
            try:
                if accrual:
                    client.call('auth', 'accrual', body)
                else:
                    client.call('auth', 'withdrawal', body)
            except exceptions.ValidationError as e: raise e
            except exceptions.APIException as e: raise e
            except Exception as e:
                raise exceptions.APIException(e)

        warrior = self.user.cards.filter(card__id=data.get('warrior_card_id'))
        warrior = warrior.first().card.content_object if warrior else None

        if warrior:
            warrior.experience += data.get('warrior_exp')
            warrior.progress += data.get('progress')
            hours, minutes, seconds = map(
                int, str(data.get('injury_time')).split(':')
            )
            warrior.available_from = datetime.now() + timedelta(hours=hours,
                                                                minutes=minutes,
                                                                seconds=seconds)
            warrior.save()

        for potion_card_id, count in data.get('used_potions'):
            potion_set = self.user.cards.get(card__id=potion_card_id) \
                if self.user.cards.filter(card__id=potion_card_id) else None

            if potion_set:
                potion_set.count -= count
                potion_set.save()

        return data
