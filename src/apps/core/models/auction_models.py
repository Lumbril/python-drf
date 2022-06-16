from apps.core.models import CardSet, Currency

from collections import OrderedDict

from django.conf import settings

from django.db import models


class AuctionLot(models.Model):
    """Лот аукциона"""

    lot = models.ForeignKey(CardSet, null=True, on_delete=models.SET_NULL, verbose_name='Лот')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name='Продавец')
    currency = models.ForeignKey(Currency, null=True, on_delete=models.SET_NULL, verbose_name='Валюта')
    cost = models.PositiveIntegerField(null=True, default=0, verbose_name='Стоимость')
    date_created = models.DateTimeField(null=True, auto_now_add=True, verbose_name='Создано')
    date_edited = models.DateTimeField(null=True, auto_now=True, verbose_name='Изменено')
    date_deleted = models.DateTimeField(null=True, blank=True, verbose_name='Удалено')

    def __str__(self):
        return self.lot.__str__()

    def get_cost(self):
        return OrderedDict([('currency', self.currency), ('amount', self.cost)])

    def personal_lot(self, user):
        return True if self.user == user else False

    class Meta:
        db_table = 'auction_lots'
        verbose_name = 'Лот'
        verbose_name_plural = 'Аукционные лоты'
