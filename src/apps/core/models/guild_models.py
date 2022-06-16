from django.utils.translation import gettext_lazy as _

from django.conf import settings

from packs import tag_generator

from django.db import models


class GuildRank(models.Model):
    """Звание в гильдии"""

    name_system = models.CharField(max_length=100, null=True, unique=True, db_index=True,
                                   verbose_name='Название звания (системное)')
    name = models.CharField(max_length=100, null=True, unique=True, verbose_name='Название звания')
    worth = models.IntegerField(default=0, unique=True, null=True, verbose_name='Значимость роли')
    opportunity_accept_application = models.BooleanField(default=False, verbose_name='Может принимать/отклонять заявки')

    def __str__(self): return str(self.name_system)

    class Meta:
        db_table = 'guild_ranks'
        verbose_name = 'Звание'
        verbose_name_plural = '(Гильдия) Звания'


class Country(models.Model):
    """Страна"""

    country = models.CharField(max_length=255, null=True, unique=True, db_index=True, verbose_name='Страна')

    def __str__(self): return str(self.country)

    class Meta:
        db_table = 'countries'
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'


class Guild(models.Model):
    """Гильдия"""

    name = models.CharField(max_length=255, null=True, db_index=True, verbose_name='Наименование')
    max_count_players = models.PositiveIntegerField(default=50, verbose_name='Максимальное количество игроков')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    icon = models.CharField(max_length=255, null=True, blank=True, verbose_name='Иконка')
    type = models.BooleanField(default=True, verbose_name='Открытая гильдия')
    location = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, verbose_name='Локация')
    tag = models.CharField(max_length=9, null=True, unique=True, blank=True, verbose_name='Тэг')
    threshold = models.PositiveIntegerField(default=0, verbose_name='Ограничение')
    date_created = models.DateTimeField(null=True, auto_now_add=True, verbose_name='Дата создания')
    date_edited = models.DateTimeField(null=True, auto_now=True, verbose_name='Изменено')
    date_deleted = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления')

    def __str__(self): return str(self.name)

    def get_icon(self): return settings.MEDIA_ADDRESS + self.icon if self.icon else None

    def save(self, *args, **kwargs):
        if self.tag is None:
            self.tag = tag_generator(model=type(self))
        super().save(*args, **kwargs)

    @property
    def power(self):
        players_qs = self.players.filter(active=True)\
            .select_related('guild', 'player')\
            .prefetch_related('player__cards') \
            .annotate(total_power=models.Sum('player__cards__card__total_power'))
        power = 0
        for guild_player in players_qs:
            power += guild_player.total_power
        return power

    class Meta:
        db_table = 'guilds'
        verbose_name = 'Гильдия'
        verbose_name_plural = '(Гильдия) Гильдии'


class GuildPlayer(models.Model):
    """Игрок гильдии"""

    guild = models.ForeignKey(Guild, on_delete=models.SET_NULL, null=True,
                              verbose_name='Гильдия', related_name='players')
    player = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True, on_delete=models.SET_NULL, null=True,
                               verbose_name='Игрок', related_name='guild_player')
    rank = models.ForeignKey(GuildRank, on_delete=models.SET_NULL, null=True, verbose_name='Ранг игрока')
    active = models.BooleanField(default=True, verbose_name='Игрок в гильдии')
    date_ban = models.DateTimeField(blank=True, null=True, verbose_name='Время до которого нельзя писать')

    def __str__(self): return '{0.guild} - {0.player}'.format(self)

    class Meta:
        db_table = 'guild_players'
        verbose_name = 'Игрок'
        verbose_name_plural = '(Гильдия) Игроки'


class GuildApplication(models.Model):
    """Заявка и приглашение в гильдию"""

    class Type(models.TextChoices):
        INVITATION = 'INVITATION', _('Invitation')
        APPLICATION = 'APPLICATION', _('Application')

    class Status(models.TextChoices):
        NEW = 'NEW', _('New')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')
        WITHDRAWN = 'WITHDRAWN', _('Withdrawn')

    type = models.CharField(max_length=100, null=True, choices=Type.choices, verbose_name='Тип заявки')
    status = models.CharField(max_length=100, null=True, choices=Status.choices, verbose_name='Статус заявки')
    to = models.ForeignKey(Guild, on_delete=models.SET_NULL, null=True,
                           verbose_name='В какую гильдию', related_name='applications')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                               related_name='author', verbose_name='Автор')
    whom = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Кого')
    date_created = models.DateTimeField(null=True, auto_now_add=True, verbose_name='Дата создания')
    date_edited = models.DateTimeField(null=True, auto_now=True, verbose_name='Дата изменения')
    date_deleted = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления')

    def __str__(self): return '{0.to} - {0.whom}'.format(self)

    class Meta:
        db_table = 'guild_applications'
        verbose_name = 'Заявка'
        verbose_name_plural = '(Гильдия) Заявки'
