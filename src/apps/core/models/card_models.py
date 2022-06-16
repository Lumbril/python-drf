from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from rest_framework import exceptions

from collections import OrderedDict

from .storage_models import Storage

from django.conf import settings

from datetime import datetime

from django.db import models

import random

import copy


class Card(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, verbose_name='Вид')
    object_id = models.PositiveIntegerField(null=True, verbose_name='ID объекта')
    content_object = GenericForeignKey('content_type', 'object_id')
    total_power = models.PositiveIntegerField(verbose_name='Вес карты', default=0)

    def __str__(self):
        model_name_enum = {
            WarriorCard.__name__.lower(): 'Карта Война',
            WeaponCard.__name__.lower(): 'Карта Оружия',
            ArmorCard.__name__.lower(): 'Карта Брони',
            PotionCard.__name__.lower(): 'Карта Зелья',
            Ticket.__name__.lower(): 'Билет',
            'chest': 'Карта Сундука',
        }

        return f'{model_name_enum[self.content_type.model]} – {self.content_object}'

    class Meta:
        db_table = 'cards'
        verbose_name = 'Карта'
        verbose_name_plural = 'Карты'


class DamageType(models.Model):
    """Тип урона"""

    name = models.CharField(max_length=255, null=True, unique=True, db_index=True, verbose_name='Название')

    def __str__(self): return str(self.name)

    class Meta:
        db_table = 'damage_types'
        verbose_name = '(Карта) (Оружие) Вид урона'
        verbose_name_plural = '(Карты) (Оружия) Виды урона'


class CardType(models.Model):
    """Тип карты"""

    name = models.CharField(max_length=255, null=True, unique=True, db_index=True, verbose_name='Название')
    system_name = models.CharField('Системное название', max_length=255, null=True, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    icon = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Иконка')
    rank = models.PositiveIntegerField(default=1, verbose_name='Ранг эволюции', blank=True)
    damage_type = models.ForeignKey(DamageType, on_delete=models.SET_NULL, null=True,
                                    blank=True, verbose_name='Вид урона')
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, verbose_name='Относится к виду')

    combat_card = models.BooleanField(default=True, verbose_name='Боевая карта')

    def __str__(self):
        if self.content_type and self.content_type.model == WarriorCard.__name__.lower():
            return f'"{self.name}" Ранг: {self.rank}'
        return f'"{self.name}"'

    def get_icon(self): return settings.MEDIA_ADDRESS + self.icon.url if self.icon else None

    def clean(self):
        if self.content_type and self.content_type.model == WarriorCard.__name__.lower():
            if not self.rank:
                raise ValidationError("Для карты война необходимо указать ранг")

    class Meta:
        db_table = 'card_types'
        verbose_name = '(Карта) Вид'
        verbose_name_plural = '(Карты) Виды'


class Element(models.Model):
    """Стихия"""

    name = models.CharField(max_length=255, null=True, unique=True, db_index=True, verbose_name='Название')
    system_name = models.CharField(max_length=50, null=True, unique=True, db_index=True, verbose_name='Системное название')
    groups = models.CharField(max_length=255, null=True, verbose_name='Принадлежность')
    icon = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Иконка')

    def __str__(self): return str(self.name)

    def get_icon(self): return settings.MEDIA_ADDRESS + self.icon.url if self.icon else None

    class Meta:
        db_table = 'elements'
        verbose_name = '(Карта) Стихия'
        verbose_name_plural = '(Карты) Стихии'


class SpecialType(models.Model):
    """Особенный эффект"""

    name = models.CharField(max_length=255, db_index=True, verbose_name='Название')
    system_name = models.CharField(max_length=255, db_index=True, verbose_name='Системное название')
    icon = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Иконка')
    to_enemy = models.BooleanField(default=False, verbose_name='Действует на противника')

    def __str__(self): return str(self.name)

    def get_icon(self): return settings.MEDIA_ADDRESS + self.icon.url if self.icon else None

    class Meta:
        db_table = 'special_types'
        verbose_name = '(Карта) (Эффект) Вид'
        verbose_name_plural = '(Карты) (Эффекты) Виды'


class Special(models.Model):
    """Особенный эффект"""

    type = models.ForeignKey(SpecialType, on_delete=models.CASCADE, verbose_name='Вид эффекта')
    value = models.FloatField(default=0, verbose_name='Значение', validators=[MinValueValidator(0.0)])
    percentages = models.BooleanField(default=False, verbose_name='В процентах')
    duration = models.IntegerField(default=0, verbose_name='Длительность эффекта в раундах',
                                   help_text='Если < 0, то действует весь бой(кроме восстановления/понижения зворовья)')

    def __get_duration_str(self):
        if self.duration < 0:
            return 'На весь матч'
        elif self.duration == 0:
            return 'Мгновенно'
        return f'{self.duration} ходов'

    def __str__(self):
        return f'{self.type} {self.value}{"%" if self.percentages else ""}' \
               f'({"На противника" if self.type.to_enemy else "На себя"})[{self.__get_duration_str()}]'

    class Meta:
        db_table = 'specials'
        verbose_name = '(Карта) (Эффект) Эффект'
        verbose_name_plural = '(Карты) (Эффекты) Эффекты'


class Currency(models.Model):

    name = models.CharField('Читаемое название', max_length=255, null=True, unique=True, db_index=True)
    system_name = models.CharField('Системное название', max_length=255, null=True, unique=True, db_index=True)

    def __str__(self): return str(self.name)

    class Meta:
        db_table = 'currencies'
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'


class AbstractCard(models.Model):

    name = models.CharField(max_length=255, null=True, db_index=True, verbose_name='Название')
    icon = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Иконка')
    type = models.ForeignKey(CardType, on_delete=models.SET_NULL, null=True, verbose_name='Вид карты')
    currency_purchase = models.ForeignKey(Currency, null=True, related_name='%(class)s_purchase',
                                          on_delete=models.SET_NULL, verbose_name='Валюта покупки')
    amount_purchase = models.FloatField('Количество', null=True)
    currency_sale = models.ForeignKey(Currency, null=True, related_name='%(class)s_sale',
                                      on_delete=models.SET_NULL, verbose_name='Валюта продажи')
    amount_sale = models.FloatField('Количество', null=True)
    date_created = models.DateTimeField(default=datetime.now, verbose_name='Создано')
    date_edited = models.DateTimeField(default=datetime.now, verbose_name='Изменено')
    date_deleted = models.DateTimeField(null=True, blank=True, verbose_name='Удалено')
    card = GenericRelation('Card')

    def __str__(self): return str(self.name)

    def get_icon(self):
        if self.icon is None:
            return self.type.get_icon() if self.type else None
        return settings.MEDIA_ADDRESS + self.icon.url

    def get_cost(self):
        return OrderedDict([('currency', self.currency_purchase), ('amount', self.amount_purchase)])

    def get_coin(self):
        return OrderedDict([('currency', self.currency_sale), ('amount', self.amount_sale)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not Card.objects.filter(content_type=ContentType.objects.get(model=type(self).__name__.lower()),
                                   object_id=self.pk).exists():
            new_card = Card(content_type=ContentType.objects.get(model=type(self).__name__.lower()),
                            object_id=self.pk)
            new_card.save()

    def delete(self, *args, **kwargs):
        if self.card.first():
            self.card.delete()
        super().delete(*args, **kwargs)

    class Meta:
        abstract = True
        verbose_name = 'Абстрактная карта'
        verbose_name_plural = 'Абстрактные карты'


class PotionSize(models.Model):

    name = models.CharField(max_length=255, null=True, unique=True, db_index=True, verbose_name='Размер')
    system_name = models.CharField(max_length=100, null=True,
                                   unique=True, db_index=True, verbose_name='Системное название размера')

    def __str__(self): return str(self.name)

    class Meta:
        db_table = 'potion_sizes'
        verbose_name = '(Карта) (Зелье) Размер'
        verbose_name_plural = '(Карты) (Зелья) Размеры'


class PotionCard(AbstractCard):
    """Эликсир"""

    level = models.PositiveIntegerField(default=1, verbose_name='Ранг зелья')
    size = models.ForeignKey(PotionSize, on_delete=models.SET_NULL, null=True, verbose_name='Размер')
    specials = models.ManyToManyField(Special, db_table='potion_specials', blank=True, verbose_name='Особые эффекты')

    def __str__(self): return "{name} ({size})".format(name=self.name, size=self.size.name)

    class Meta:
        db_table = 'potion_cards'
        verbose_name = '(Карта) Зелье'
        verbose_name_plural = '(Карты) Зелья'


class WeaponCard(AbstractCard):
    """Оружие"""

    damage = models.PositiveIntegerField(default=1, verbose_name='Урон')
    req_agility = models.PositiveIntegerField(default=1, verbose_name='Требуемая ловкость')
    base = models.BooleanField(default=True, verbose_name='Магазинная')
    req_strength = models.PositiveIntegerField(default=1, verbose_name='Требуемая сила')
    req_vitality = models.PositiveIntegerField(default=1, verbose_name='Требуемая живучесть')
    critical_chance = models.FloatField(default=0.0, verbose_name='Шанс критического удара')
    req_intelligence = models.PositiveIntegerField(default=1, verbose_name='Требуемы интеллект')
    element = models.ForeignKey(Element, on_delete=models.SET_NULL, null=True, verbose_name='Стихия')
    ratio_agility = models.FloatField(default=1, verbose_name='Коэффициент ловкости')
    ratio_strength = models.FloatField(default=1, verbose_name='Коэффициент силы')
    ratio_intelligence = models.FloatField(default=1, verbose_name='Коэффициент интеллекта')
    ratio_vitality = models.FloatField(default=1, verbose_name='Коэффициент живучести')
    ability_cooldown = models.PositiveIntegerField(default=3, verbose_name='Перезарядка способности в ходах')
    specials = models.ManyToManyField(Special, db_table='weapon_specials', blank=True, verbose_name='Особые эффекты')
    attack_immediately = models.BooleanField(default=False, verbose_name='Атака сразу')
    ability_name = models.CharField(default='null', verbose_name='Название способности', max_length=255)

    def __str__(self): return '{0.name} #{0.id}'.format(self) if not self.base else self.name

    @property
    def power(self):
        return self.damage

    def clone(self):
        obj = copy.copy(self)
        obj.pk = None
        obj.id = None
        obj.base = False
        obj.save()
        obj.specials.set(self.specials.all())
        return obj

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        card = self.card.first()
        card.total_power = self.power
        card.save()

    class Meta:
        db_table = 'weapon_cards'
        verbose_name = '(Карта) Оружие'
        verbose_name_plural = '(Карты) Оружия'


class ArmorCard(AbstractCard):
    """Броня"""

    req_agility = models.PositiveIntegerField(default=1, verbose_name='Требуемая ловкость')
    req_strength = models.PositiveIntegerField(default=1, verbose_name='Требуемая сила')
    base = models.BooleanField(default=True, verbose_name='Магазинная')
    req_vitality = models.PositiveIntegerField(default=1, verbose_name='Требуемая живучесть')
    req_intelligence = models.PositiveIntegerField(default=1, verbose_name='Требуемый интеллект')
    damage_reduction = models.PositiveIntegerField(default=1, verbose_name='Уменьшение урона')
    element = models.ForeignKey(Element, on_delete=models.SET_NULL, null=True, verbose_name='Стихия')
    specials = models.ManyToManyField(Special, db_table='armor_specials', blank=True, verbose_name='Особые эффекты')
    ability_cooldown = models.PositiveIntegerField(default=3, verbose_name='Перезарядка способности в ходах')
    ability_name = models.CharField(null=True, verbose_name='Название способности', max_length=255)

    def __str__(self): return '{0.name} #{0.id}'.format(self) if not self.base else self.name

    @property
    def power(self):
        return self.damage_reduction

    def clone(self):
        obj = copy.copy(self)
        obj.pk = None
        obj.id = None
        obj.base = False
        obj.save()
        obj.specials.set(self.specials.all())
        return obj

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        card = self.card.first()
        card.total_power = self.power
        card.save()

    class Meta:
        db_table = 'armor_cards'
        verbose_name = '(Карта) Броня'
        verbose_name_plural = '(Карты) Брони'


class Evolution(models.Model):
    """Эволюции"""
    """Если depends_on null, это значит, что в эволюции это самый первый этап"""
    base_type = models.ForeignKey(CardType, on_delete=models.SET_NULL, related_name='base_types',
                                  null=True, blank=True, verbose_name='Исходный подтип')
    next_type = models.ForeignKey(CardType, on_delete=models.SET_NULL, related_name='next_types',
                                  null=True, blank=True, verbose_name='Эволюционирует в')
    req_agility = models.PositiveIntegerField(default=0, verbose_name='Требуемая ловкость')
    req_strength = models.PositiveIntegerField(default=0, verbose_name='Требуемая сила')
    req_vitality = models.PositiveIntegerField(default=0, verbose_name='Требуемая живучесть')
    req_intelligence = models.PositiveIntegerField(default=0, verbose_name='Требуемый интеллект')
    req_defense = models.PositiveIntegerField(default=0, verbose_name='Требуемый защиты')
    delta_agility = models.IntegerField(default=0, verbose_name='Изменение ловкости')
    delta_strength = models.IntegerField(default=0, verbose_name='Изменение силы')
    delta_vitality = models.IntegerField(default=0, verbose_name='Изменение живучести')
    delta_intelligence = models.IntegerField(default=0, verbose_name='Изменение интеллекта')
    delta_defense = models.IntegerField(default=0, verbose_name='Изменение защиты')
    specials = models.ManyToManyField(Special, db_table='evolution_specials', blank=True, verbose_name='Особые эффекты')

    def __str__(self): return f'Эволюция от {self.base_type} к {self.next_type}'

    @property
    def requirements(self):
        return self.req_agility, self.req_strength, self.req_vitality, self.req_intelligence, self.req_defense

    def clean(self):
        if self.base_type and self.next_type:
            if self.base_type.rank + 1 != self.next_type.rank:
                raise ValidationError("Неверные ранги эволюции")

    class Meta:
        db_table = 'evolutions'
        verbose_name = '(Карта) (Воин) Эволюция'
        verbose_name_plural = '(Карты) (Воины) Эволюции'


class WarriorCard(AbstractCard):
    """Воин"""

    level = models.PositiveIntegerField(default=1, verbose_name='Уровень')
    experience = models.PositiveIntegerField(default=0, verbose_name='Опыт')
    progress = models.FloatField(default=0, verbose_name='Прогресс')
    base = models.BooleanField(default=True, verbose_name='Магазинная')
    primary_element = models.ForeignKey(Element, on_delete=models.SET_NULL, null=True,
                                        related_name='primary_element', verbose_name='Основная стихия')
    secondary_element = models.ForeignKey(Element, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='secondary_element', verbose_name='Дополнительная стихия')
    defense = models.PositiveIntegerField(default=1, verbose_name='Защита')
    agility = models.PositiveIntegerField(default=1, verbose_name='Ловкость')
    potential = models.PositiveIntegerField(default=1, verbose_name='Потенциал')
    strength = models.PositiveIntegerField(default=1, verbose_name='Сила')
    vitality = models.PositiveIntegerField(default=1, verbose_name='Живучесть')
    intelligence = models.PositiveIntegerField(default=1, verbose_name='Интеллект')
    specials = models.ManyToManyField(Special, db_table='warrior_specials', verbose_name='Особые эффекты')
    available_from = models.DateTimeField(null=True, blank=True, verbose_name='Достпуна от')

    def __str__(self): return '{0.name} #{0.id}'.format(self) if not self.base else self.name

    @property
    def stats(self):
        return self.agility, self.strength, self.vitality, self.intelligence, self.defense

    @property
    def power(self):
        return sum((self.agility, self.strength, self.potential, self.intelligence, self.defense, self.vitality))
    
    @property
    def injured(self):
        if not self.available_from:
            return False
        return True if self.available_from > datetime.now() else False
    
    def is_available_evolution(self, evolution):
        if self.potential <= 0:
            return False
        current_stats = self.stats
        if not evolution.next_type:
            return False
        requirements = evolution.requirements
        for index in range(len(current_stats)):
            if current_stats[index] < requirements[index]:
                return False
        return True

    def clone(self):
        obj = copy.copy(self)
        obj.pk = None
        obj.id = None
        obj.base = False
        obj.save()
        obj.specials.set(self.specials.all())
        return obj

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        card = self.card.first()
        card.total_power = self.power
        card.save()

    def get_next_evolutions(self):
        return self.type.base_types.all()

    def upgrade(self, distribution):
        stats_keys = list(distribution.keys())
        stats_values = list(distribution.values())
        intervals = dict()
        for index in range(len(stats_keys)):
            intervals[stats_keys[index]] = sum(stats_values[0:index + 1])
        result = random.uniform(0, 100)
        for key, value in intervals.items():
            if result <= value:
                stat = getattr(self, key)
                setattr(self, key, stat + 1)
                self.save()
                return {
                    'attribute': key,
                    'before': stat,
                    'after': stat + 1
                }

    def evolve(self, evolution):
        if not self.is_available_evolution(evolution):
            raise exceptions.ValidationError('Requirements not met')
        self.agility += evolution.delta_agility
        self.strength += evolution.delta_strength
        self.vitality += evolution.delta_vitality
        self.intelligence += evolution.delta_intelligence
        self.defense += evolution.delta_defense
        self.type = evolution.next_type
        for special in self.specials.all():
            same_specials = Special.objects.filter(type=special.type, value__gt=special.value).order_by('value')
            if same_specials:
                self.specials.remove(special)
                self.specials.add(same_specials.first())
        for special in evolution.specials.all():
            if special.type not in [special.type for special in self.specials.all()]:
                element_key = special.type.system_name.split(':')[0]
                for base_special in self.specials.all():
                    element = Element.objects.filter(system_name=base_special.type.system_name.split(':')[0])
                    element_groups = element.first().groups.split('/') if element else tuple()
                    if element_key in element_groups:
                        self.specials.add(special)
                        break
        self.potential -= 1
        self.save()

    class Meta:
        db_table = 'warrior_cards'
        verbose_name = '(Карта) Воин'
        verbose_name_plural = '(Карты) Воины'


class TicketCurrency(models.Model):

    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, verbose_name='Валюта')
    amount = models.FloatField('Количество', null=True)

    def __str__(self): return f'{self.currency} - {self.amount}'

    class Meta:
        db_table = 'currencies_tickets'
        verbose_name = '(Карта) (Билет) Валюта'
        verbose_name_plural = '(Карты) (Билеты) Валюты'


class TicketCard(models.Model):

    card = models.ForeignKey(Card, on_delete=models.CASCADE, verbose_name='Карта')
    amount = models.FloatField('Количество', null=True)

    def __str__(self): return f'{self.card} - {self.amount}'

    class Meta:
        db_table = 'cards_tickets'
        verbose_name = '(Карта) (Билет) Карта'
        verbose_name_plural = '(Карты) (Билеты) Карты'


class Ticket(AbstractCard):
    """Билет"""

    base = models.BooleanField(default=True, verbose_name='Магазинная')
    currencies = models.ManyToManyField(TicketCurrency, db_table='ticket_currencies', verbose_name='Валюты')
    cards = models.ManyToManyField(TicketCard, db_table='ticket_cards', verbose_name='Карты')
    date_activation = models.DateTimeField(null=True, blank=True, verbose_name='Активировано')

    def __str__(self): return '{0.name} #{0.id}'.format(self) if not self.base else self.name

    def clone(self):
        obj = copy.copy(self)
        obj.pk = None
        obj.id = None
        obj.base = False
        obj.save()
        obj.cards.set(self.cards.all())
        obj.currencies.set(self.currencies.all())
        return obj

    class Meta:
        db_table = 'tickets'
        verbose_name = '(Карта) Билет'
        verbose_name_plural = '(Карты) Билеты'
