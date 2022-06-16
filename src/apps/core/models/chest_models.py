from django.core.exceptions import ValidationError

from .card_models import Card, AbstractCard, Currency

from django.db import models

import random


class Drop(models.Model):
    """Элемент сундука"""

    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Карта')
    distribution = models.FloatField(default=0, verbose_name='Распределение')
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Валюта')
    amount = models.FloatField(null=True, blank=True, verbose_name='Количество валюты')

    def __str__(self):
        if self.card:
            return f'{str(self.card)} {self.distribution}'
        elif self.currency:
            return f'{self.amount} {self.currency} {self.distribution}'
        return 'Deleted'

    def get_currency(self):
        if self.currency:
            return {
                'name': self.currency.name,
                'system_name': self.currency.system_name,
                'amount': self.amount
            }
        return None

    def clean(self):
        if self.card and self.currency:
            raise ValidationError('Невозможно выпадение предмета и валюты одновременно (Добавить по отдельности)')
        elif not self.card and not (self.currency and self.amount):
            raise ValidationError('Для выпадения валюты нажно заполнить оба поля Валюта и Количество')
        elif not self.card and not self.currency:
            raise ValidationError('Не выбран ни один предмет')

    class Meta:
        db_table = 'drops'
        verbose_name = '(Карты) (Сундук) Элемент набора'
        verbose_name_plural = '(Карты) (Сундуки) Элементы набора'


class Item(models.Model):
    """Отвечает за набор из которого выпадет предмет"""

    items = models.ManyToManyField(Drop, db_table='item_items', blank=True, verbose_name='Набор карт')

    def __str__(self): return f"Items: {' ; '.join([str(item) for item in self.items.all()])}"

    class Meta:
        db_table = 'items'
        verbose_name = '(Карты) (Сундук) Набор карт'
        verbose_name_plural = '(Карты) (Сундуки) Наборы карт'


class Chest(AbstractCard):
    """Сундук"""

    items = models.ManyToManyField(Item, db_table='chest_items', blank=True, verbose_name='Содержимое сундука')

    def open(self) -> list:
        selection = list()
        for items in self.items.all():
            intervals = dict()
            interval_value = 0
            for item in items.items.all():
                interval_value += item.distribution
                intervals[str(item.id)] = interval_value
            selection.append(intervals)
        drop_items = list()
        for interval in selection:
            if list(interval.values())[-1] == 0:
                continue
            random_value = random.uniform(0, list(interval.values())[-1])
            for key, value in interval.items():
                if random_value <= value:
                    drop_items.append(Drop.objects.get(pk=int(key)))
                    break
        return drop_items

    class Meta:
        db_table = 'chests'
        verbose_name = '(Карта) Сундук'
        verbose_name_plural = '(Карты) Сундуки'
