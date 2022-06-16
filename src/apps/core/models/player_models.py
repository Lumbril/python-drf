from django.contrib.auth.models import AbstractUser, Permission, Group

from .card_models import Card, CardType, Ticket

from django.conf import settings

from django.db import models


class Level(models.Model):
    """Уровень"""

    level = models.PositiveIntegerField(unique=True, null=True, verbose_name='Уровень')
    exp = models.PositiveIntegerField(default=1000, verbose_name='Опыт для следущего уровня')

    def __str__(self):
        return f"Уровень {self.level}, переход нв следующий после {self.exp} опыта"

    class Meta:
        db_table = 'levels'
        verbose_name = 'Уровень'
        verbose_name_plural = 'Уровни'


class User(AbstractUser):

    auth_id = models.IntegerField('Auth ID', unique=True, db_index=True, blank=True, null=True)
    first_name = models.CharField('Имя', max_length=150, blank=True, null=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True, null=True)
    email = models.EmailField('Почта', max_length=255, blank=True, null=True)
    icon = models.CharField('Иконка', max_length=255, blank=True, null=True)
    enter_ticket = models.OneToOneField(Ticket, on_delete=models.SET_NULL, null=True, blank=True, 
                                        related_name='user', verbose_name='Входной билет')
    groups = models.ManyToManyField(Group, db_table='user_groups', blank=True,
                                    help_text='The groups this user belongs to. '
                                    'A user will get all permissions granted to each of their groups.',
                                    related_name='groups', related_query_name='user')

    user_permissions = models.ManyToManyField(Permission, db_table='user_permissions', blank=True,
                                              help_text='Specific permissions for this user.',
                                              related_name='permissions', related_query_name='user')

    level = models.ForeignKey(Level, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Уровень')
    personal_exp = models.PositiveIntegerField(default=0, verbose_name='Текущий опыт пользователя')
    card_exp = models.PositiveIntegerField(default=0, verbose_name='Свободный опыт карт')

    def get_icon(self): return settings.MEDIA_ADDRESS + self.icon if self.icon else None

    def save(self, *args, **kwargs):
        if self.level is None:
            lvl = Level.objects.filter(level=1)

            if not lvl.exists():
                first_lvl = Level()
                first_lvl.level = 1
                first_lvl.exp = 1000
                first_lvl.save()
                lvl = first_lvl
            else:
                lvl = lvl.first()

            self.level = lvl
        super().save(*args, **kwargs)

    def get_cards_list(self):
        for card_set in self.cards.filter(date_deleted__isnull=True):
            yield card_set.card

    def get_cards_no_auction(self):
        for card_set in self.cards.filter(is_auction=False, date_deleted__isnull=True):
            yield card_set.card

    def get_potion_types(self):
        types_id = list()
        for card_set in self.cards.all():
            card_type = card_set.card.content_object.type
            if card_type.content_type.model == 'potioncard' and card_type.id not in types_id:
                types_id.append(card_type.id)
        return CardType.objects.filter(id__in=types_id)

    @property
    def power(self):
        cards = self.cards.all().select_related('card', 'user', 'card__content_type')
        power = sum([card_set.card.total_power * card_set.count for card_set in cards])
        return power

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = '(Пользователь) Пользователи'


class CardSet(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Принадлежит', related_name='cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, verbose_name='Карта')
    count = models.PositiveIntegerField(default=1, verbose_name='Количество')
    date_created = models.DateTimeField(null=True, auto_now_add=True, verbose_name='Создано')
    date_edited = models.DateTimeField(null=True, auto_now=True, verbose_name='Изменено')
    date_deleted = models.DateTimeField(null=True, blank=True, verbose_name='Удалено')

    @property
    def check_is_auction(self):
        from .auction_models import AuctionLot

        return AuctionLot.objects.filter(lot=self, date_deleted__isnull=True).exists()

    def __str__(self): return f"{self.user} | {self.card} Количество: {self.count}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.count == 0:
            self.delete()

    class Meta:
        db_table = 'card_sets'
        verbose_name = '(Пользователь) Карта'
        verbose_name_plural = '(Пользователь) Карты'
