from apps.core.models import Guild

from django.conf import settings

from django.db import models


class ChatLog(models.Model):

    guild = models.ForeignKey(Guild, on_delete=models.SET_NULL, null=True,
                              blank=True, verbose_name='Гильдия', related_name='chat_log')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Пользователь', related_name='messages')
    time = models.DateTimeField(null=True, auto_now_add=True, verbose_name='Время')
    message = models.TextField(verbose_name='Сообщение')

    def __str__(self): return f"{self.guild} - {self.user} - {self.time}"

    class Meta:
        db_table = 'chat_logs'
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
