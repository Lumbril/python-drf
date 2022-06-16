from django.conf import settings

from datetime import datetime

from django.db import models


class BattleLog(models.Model):

    key = models.UUIDField(null=True, blank=True, verbose_name='Временный ключ матча')
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='matches_user1',
                              blank=False, verbose_name='Первый пользователь')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='matches_user2',
                              blank=False, verbose_name='Второй пользователь')

    user1_data = models.TextField(verbose_name='Данные первого пользователя', null=True)
    user2_data = models.TextField(verbose_name='Данные второго пользователя', null=True)

    time = models.DateTimeField(default=datetime.now, verbose_name='Время')

    def __str__(self):
        return f'{self.key} {self.time} {self.user1} {self.user2}'

    class Meta:
        db_table = 'battle_logs'
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'


class BattleRound(models.Model):

    battle = models.ForeignKey(BattleLog, on_delete=models.CASCADE, verbose_name='Матч', related_name='rounds')
    data = models.TextField(verbose_name='Данные раунда')

    def __str__(self):
        return str(self.battle)

    class Meta:
        db_table = 'battle_rounds'
        verbose_name = 'Раунд'
        verbose_name_plural = 'Раунды'
