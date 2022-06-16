from django.conf import settings

from django.db import models


class Storage(models.Model):

    media_id = models.IntegerField('Media ID', unique=True, db_index=True, blank=True, null=True)
    name = models.CharField('Название объекта', max_length=255, null=True, unique=True, db_index=True)
    url = models.CharField('Ссылка на объект', max_length=255, null=True, blank=True)

    def __str__(self): return str(self.name)

    def get_icon(self): return settings.MEDIA_ADDRESS + self.url if self.url else None

    class Meta:
        db_table = 'storage'
        verbose_name = 'Объект хранилища'
        verbose_name_plural = 'Хранилище'
