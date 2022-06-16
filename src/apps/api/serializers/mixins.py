from rest_framework import serializers


class CardSerializerMixin(metaclass=serializers.SerializerMetaclass):

    cost = serializers.SerializerMethodField()
    card_id = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()

    def get_model(self, obj):
        return obj.card.content_type.model

    def get_icon(self, obj):
        return obj.get_icon() if obj.get_icon() else None

    def get_card_id(self, obj):
        return obj.card_id if hasattr(obj, 'card_id') else obj.card.all().first().id

    def get_cost(self, obj):
        return {
            'purchase': {
                'currency': obj.currency_purchase.system_name,
                'amount': obj.amount_purchase
            },
            'sale': {
                'currency': obj.currency_sale.system_name,
                'amount': obj.amount_sale
            }
        }


class PowerSerializerMixin(metaclass=serializers.SerializerMetaclass):

    total_power = serializers.SerializerMethodField()

    def get_total_power(self, obj):
        return obj.power
