from apps.core.models import Storage

from django.conf import settings

from django.db import models


media = settings.MEDIA_ADDRESS


class Type(models.Model):
    """Тип"""

    name = models.CharField(max_length=255, null=True, verbose_name='Название')

    def __str__(self): return str(self.name)

    class Meta:
        db_table = 'types'
        verbose_name = 'Тип'
        verbose_name_plural = 'Типы'


class SystemInfo(models.Model):
    """Системная информация"""

    key = models.CharField(max_length=255, null=True, verbose_name='Ключ')
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True, verbose_name='Тип')
    icon = models.ForeignKey(Storage, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Ссылка на источник')
    text = models.TextField(default='Изображение не найдено', blank=True, null=True, verbose_name='Текст')

    def __str__(self): return str(self.type)

    def get_icon(self): return media + self.icon.url if self.icon else None

    def get_text(self): return self.text

    def get_value(self): return self.get_icon() if self.icon else self.get_text()

    class Meta:
        db_table = 'system_info'
        unique_together = ['key', 'type']
        verbose_name = 'Системная информация'
        verbose_name_plural = 'Системная информация'
