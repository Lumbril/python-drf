from django.db import models


class Language(models.Model):
    """Язык"""

    abbreviation = models.CharField(max_length=10, null=True, unique=True, db_index=True,
                                    verbose_name='Сокращенное название')
    title = models.CharField(max_length=100, null=True, unique=True, verbose_name='Полное название')

    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = 'languages'
        verbose_name = 'Язык'
        verbose_name_plural = 'Языки'


class Translate(models.Model):
    """Перевод"""

    key_translate = models.TextField(null=True, verbose_name='Ключ перевода')
    translate = models.TextField(null=True, unique=True, verbose_name='Перевод')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, verbose_name='Язык')

    def __str__(self):
        return str(self.key_translate)

    class Meta:
        db_table = 'translates'
        verbose_name = 'Перевод'
        verbose_name_plural = 'Переводы'
