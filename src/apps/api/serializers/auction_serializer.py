from .player_serializer import PlayerShortInfoSerializer

from apps.core.models import AuctionLot, CardSet

from .card_serializer import CardSetSerializer

from rest_framework import serializers


class AuctionLotSerializer(serializers.ModelSerializer):

    user = PlayerShortInfoSerializer()
    cost = serializers.SerializerMethodField()
    lot = CardSetSerializer()

    def get_cost(self, obj):
        return {
            'purchase': {
                'currency': obj.currency.system_name,
                'amount': obj.cost
            }
        }

    def to_representation(self, instance):
        rep = dict(super().to_representation(instance))
        cost = rep['cost']
        rep['lot_id'] = rep.pop('id')

        for key in rep['lot'].keys():
            rep[key] = rep['lot'][key]
        rep.pop('lot')
        rep.pop('currency')
        rep['cost'] = cost

        return rep

    class Meta:
        model = AuctionLot
        exclude = ('date_created', 'date_edited', 'date_deleted')


class AuctionLotCreateSerializer(serializers.ModelSerializer):

    card_id = serializers.IntegerField()
    currency_name = serializers.CharField()
    cost = serializers.IntegerField()

    class Meta:
        model = CardSet
        fields = ('card_id', 'currency_name', 'cost')


class AuctionLotPurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuctionLot
        fields = ('id',)
