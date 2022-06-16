from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.core.models import *

from .serializer import *
from .mixins import *


UserModel = get_user_model()


class ElementSerializer(serializers.ModelSerializer):

    icon = serializers.SerializerMethodField()

    def get_icon(self, obj):
        return obj.get_icon() if obj.get_icon() else None

    class Meta:
        model = Element
        fields = '__all__'


class CardTypeSerializer(serializers.ModelSerializer):

    icon = serializers.SerializerMethodField()

    def get_icon(self, obj):
        return obj.get_icon()

    class Meta:
        model = CardType
        exclude = ('content_type',)


class SpecialTypeSerializer(serializers.ModelSerializer):

    icon = serializers.SerializerMethodField()

    def get_icon(self, obj):
        return obj.get_icon()

    class Meta:
        model = SpecialType
        exclude = ('id',)


class SpecialSerializer(serializers.ModelSerializer):

    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return SpecialTypeSerializer(obj.type).data if obj.type else None

    class Meta:
        model = Special
        exclude = ('id',)


class EvolutionSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.warrior = kwargs.get('warrior',)

    specials = serializers.SerializerMethodField()
    next_type = serializers.SlugRelatedField(slug_field='name', read_only=True)
    icon = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()

    def get_available(self, obj):
        return self.warrior.is_available_evolution(obj)

    def get_specials(self, obj):
        specials = list()
        for special in self.warrior.specials.all():
            same_specials = Special.objects.filter(type=special.type, value__gt=special.value).order_by('value')
            if same_specials:
                specials.append(same_specials.first())
        for special in obj.specials.all():
            if special.type not in [special.type for special in self.warrior.specials.all()]:
                element_key = special.type.system_name.split(':')[0]
                for base_special in self.warrior.specials.all():
                    element = Element.objects.filter(system_name=base_special.type.system_name.split(':')[0])
                    element_groups = element.first().groups.split('/') if element else tuple()
                    if element_key in element_groups:
                        specials.append(special)
                        break
        return [SpecialSerializer(special).data for special in specials]

    def get_icon(self, obj):
        return obj.next_type.get_icon() if obj.next_type.get_icon() else None

    class Meta:
        model = Evolution
        exclude = ('base_type',)


class EvolveSerializer(serializers.Serializer):

    evolution_id = serializers.IntegerField()

    class Meta:
        fields = '__all__'


class StatsAddSerializer(serializers.Serializer):

    field_params = {'min_value': 0, 'required': False}
    agility = serializers.IntegerField(**field_params)
    strength = serializers.IntegerField(**field_params)
    intelligence = serializers.IntegerField(**field_params)
    vitality = serializers.IntegerField(**field_params)
    defense = serializers.IntegerField(**field_params)

    def validate(self, data):
        stats = dict(data)
        if len(stats) > 1:
            raise serializers.ValidationError('Cannot be more than 1 field')
        return super().validate(data)


class StatsSerializer(serializers.ModelSerializer):

    def __init__(self, additional, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.additional = additional

    stats = serializers.SerializerMethodField()

    def get_stats(self, obj):
        ratio = {  # TODO: вынос в конфиг
            'card_exp': 15,
            'percentages': 5,
        }
        power = obj.power - obj.potential
        stats = {
            'agility': obj.agility / power,
            'strength': obj.strength / power,
            'intelligence': obj.intelligence / power,
            'vitality': obj.vitality / power,
            'defense': obj.defense / power,
        }
        total_points = 0
        if self.additional:
            attr = list(self.additional.keys())[0]
            total_points = self.additional[attr] // ratio['card_exp']
            increase_value = total_points * ratio['percentages'] / 100
            decrease_value = increase_value
            stats[attr] += increase_value
            average_decrease = decrease_value / self.count_to_subtract(stats)
            while decrease_value > 0:
                minimum = min([stats[key] if key != attr and stats[key] > 0 else 100 for key in stats.keys()])
                if minimum < average_decrease:
                    for key in stats.keys():
                        if key == attr:
                            continue
                        if stats[key] == minimum:
                            decrease_value -= stats[key]
                            stats[key] = 0
                            average_decrease = decrease_value / self.count_to_subtract(stats)
                else:
                    for key in stats.keys():
                        if key == attr:
                            continue
                        stats[key] -= average_decrease
                    break

        for key in stats.keys():
            stats[key] = self.normalize(round(stats[key] * 100, 2))
        total_cost = total_points * ratio['card_exp']
        warrior_exp = total_cost if obj.experience >= total_cost else obj.experience
        stats['cost'] = {
            'warrior_exp': warrior_exp,
            'user_card_exp': total_cost - warrior_exp,
            'total_cost': total_cost
        }
        stats['ratio'] = ratio
        return stats

    @staticmethod
    def normalize(value: float) -> float:
        if value < 0:
            return 0
        elif value > 100:
            return 100
        return value

    @staticmethod
    def count_to_subtract(obj: dict) -> int:
        count = -1
        for value in obj.values():
            if value > 0:
                count += 1
        return count if count != 0 else 1

    def to_representation(self, instance):
        return super().to_representation(instance)['stats']

    class Meta:
        model = WarriorCard
        fields = ('stats',)


class WarriorCardSerializer(serializers.ModelSerializer, CardSerializerMixin, PowerSerializerMixin):

    primary_element = ElementSerializer(read_only=True)
    secondary_element = ElementSerializer(read_only=True)
    specials = SpecialSerializer(read_only=True, many=True)
    type = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    evolutions = serializers.SerializerMethodField()

    def get_type(self, obj):
        return CardTypeSerializer(obj.type).data if obj.type else None

    def get_rank(self, obj):
        return obj.type.rank

    def get_evolutions(self, obj):
        evolutions = obj.get_next_evolutions()
        if not evolutions:
            return -1
        available = 0
        for evolution in evolutions:
            if obj.is_available_evolution(evolution):
                available += 1
        return available

    class Meta:
        model = WarriorCard
        exclude = ('currency_purchase', 'amount_purchase', 'currency_sale', 'amount_sale',
                   'date_created', 'date_edited', 'date_deleted')


class WeaponCardSerializer(serializers.ModelSerializer, CardSerializerMixin, PowerSerializerMixin):

    element = ElementSerializer(read_only=True)
    type = serializers.SerializerMethodField()
    specials = SpecialSerializer(read_only=True, many=True)

    def get_type(self, obj):
        return CardTypeSerializer(obj.type).data if obj.type else None

    class Meta:
        model = WeaponCard
        exclude = ('currency_purchase', 'amount_purchase', 'currency_sale', 'amount_sale',
                   'date_created', 'date_edited', 'date_deleted')


class ArmorCardSerializer(serializers.ModelSerializer, CardSerializerMixin, PowerSerializerMixin):

    element = ElementSerializer(read_only=True)
    specials = SpecialSerializer(read_only=True, many=True)
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return CardTypeSerializer(obj.type).data if obj.type else None

    class Meta:
        model = ArmorCard
        exclude = ('currency_purchase', 'amount_purchase', 'currency_sale', 'amount_sale',
                   'date_created', 'date_edited', 'date_deleted')


class PotionCardSerializer(serializers.ModelSerializer, CardSerializerMixin):

    specials = SpecialSerializer(read_only=True, many=True)
    type = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    def get_size(self, obj):
        return {
            'name': obj.size.name,
            'system_name': obj.size.system_name,
        }

    def get_type(self, obj):
        return CardTypeSerializer(obj.type).data if obj.type else None

    class Meta:
        model = PotionCard
        exclude = ('currency_purchase', 'amount_purchase', 'currency_sale', 'amount_sale',
                   'date_created', 'date_edited', 'date_deleted')


class PotionSizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PotionSize
        fields = '__all__'


class CardObjectRelatedField(serializers.RelatedField):

    class Enum:
        Warrior = WarriorCard
        Weapon = WeaponCard
        Potion = PotionCard
        Armor = ArmorCard
        Ticket = Ticket
        Chest = Chest

    def to_representation(self, value):
        if hasattr(value, 'content_object'):
            value = value.content_object
        if isinstance(value, WarriorCard):
            serializer = WarriorCardSerializer(value)
        elif isinstance(value, WeaponCard):
            serializer = WeaponCardSerializer(value)
        elif isinstance(value, ArmorCard):
            serializer = ArmorCardSerializer(value)
        elif isinstance(value, PotionCard):
            serializer = PotionCardSerializer(value)
        elif isinstance(value, Ticket):
            serializer = TicketSerializer(value)
        elif isinstance(value, Chest):
            serializer = ChestSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


class CardPurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Card
        fields = ['id']


class CardSerializer(serializers.ModelSerializer):

    content_object = CardObjectRelatedField(read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation['content_object']

    class Meta:
        model = Card
        fields = ('content_object',)


class NFTCardSerializer(serializers.Serializer):

    token = serializers.CharField(
        write_only=True
    )        

    class Meta:
        fields = ('token',)


class CardSetSerializer(serializers.ModelSerializer):

    card = CardObjectRelatedField(read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        card = representation['card']
        card['cards_count'] = representation['count']

        return card

    class Meta:
        model = CardSet
        exclude = ('id',)


class OpenChestSerializer(serializers.Serializer):

    class Meta:
        fields = '__all__'


class DropItemSerializer:

    def __init__(self, drop):
        self.drop = drop

    @property
    def data(self):
        data = dict()
        if self.drop.card:
            data['type'] = 'card'
            data['card'] = CardSerializer(self.drop.card).data
        else:
            data['type'] = 'money'
            data['money'] = {
                'currency': self.drop.currency.system_name,
                'value': self.drop.amount
            }
        return data


class ChestSerializer(serializers.ModelSerializer, CardSerializerMixin):

    type = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Chest
        exclude = ('currency_purchase', 'amount_purchase', 'currency_sale', 'amount_sale',
                   'date_created', 'date_edited', 'date_deleted', 'items')


class ChestDropSerializer(serializers.ModelSerializer):

    chest_drop = serializers.SerializerMethodField()

    def get_chest_drop(self, obj):
        items = []
        sum_of_distribution = 0
        for drop in obj.items.all():
            sum_of_distribution += drop.distribution
        if sum_of_distribution == 0:
            return items
        for drop in obj.items.all():
            drop_context = dict()
            if drop.card:
                drop_context['card'] = CardSerializer(drop.card).data
            elif drop.currency:
                drop_context['money'] = drop.get_currency()
            items.append({
                **drop_context,
                'chance': round(100 * drop.distribution/sum_of_distribution, 2)
            })
        return items

    class Meta:
        model = Item
        exclude = ('id', 'items')


class TicketCardSerializer(serializers.ModelSerializer):

    card = serializers.SerializerMethodField()

    def get_card(self, obj):
        a = 10
        return obj.card.content_object.name

    class Meta:
        model = TicketCard
        exclude = ('id',)


class TicketCurrencySerializer(serializers.ModelSerializer):

    currency = CurrencySerializer()

    class Meta:
        model = TicketCurrency
        exclude = ('id',)


class TicketSerializer(serializers.ModelSerializer, CardSerializerMixin):

    type = serializers.SerializerMethodField()
    cards = serializers.SerializerMethodField()
    currencies = serializers.SerializerMethodField()

    def get_type(self, obj):
        return CardTypeSerializer(obj.type).data if obj.type else None

    def get_cards(self, obj):
        return TicketCardSerializer(obj.cards, many=True).data if obj.cards else None

    def get_currencies(self, obj):
        return TicketCurrencySerializer(obj.currencies, many=True).data if obj.currencies else None

    class Meta:
        model = Ticket
        exclude = ('currency_purchase', 'amount_purchase', 'currency_sale',
                   'amount_sale', 'date_created', 'date_edited', 'date_deleted',)
