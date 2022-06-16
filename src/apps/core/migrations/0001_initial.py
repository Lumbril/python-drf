import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('auth_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='Auth ID')),
                ('first_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Фамилия')),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='Почта')),
                ('icon', models.CharField(blank=True, max_length=255, null=True, verbose_name='Иконка')),
                ('personal_exp', models.PositiveIntegerField(default=0, verbose_name='Текущий опыт пользователя')),
                ('card_exp', models.PositiveIntegerField(default=0, verbose_name='Свободный опыт карт')),
                ('groups', models.ManyToManyField(blank=True, db_table='user_groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'db_table': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='ID объекта')),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype', verbose_name='Вид')),
            ],
            options={
                'verbose_name': 'Карта',
                'verbose_name_plural': 'Карты',
                'db_table': 'cards',
            },
        ),
        migrations.CreateModel(
            name='CardType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, unique=True, verbose_name='Название')),
                ('rank', models.PositiveIntegerField(blank=True, default=1, verbose_name='Ранг эволюции')),
                ('combat_card', models.BooleanField(default=True, verbose_name='Боевая карта')),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype', verbose_name='Относится к виду')),
            ],
            options={
                'verbose_name': '(Карта) Вид',
                'verbose_name_plural': '(Карты) Виды',
                'db_table': 'card_types',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(db_index=True, max_length=255, null=True, unique=True, verbose_name='Страна')),
            ],
            options={
                'verbose_name': 'Страна',
                'verbose_name_plural': 'Страны',
                'db_table': 'countries',
            },
        ),
        migrations.CreateModel(
            name='DamageType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': '(Карта) (Оружие) Вид урона',
                'verbose_name_plural': '(Карты) (Оружие) Виды урона',
                'db_table': 'damage_types',
            },
        ),
        migrations.CreateModel(
            name='Drop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distribution', models.FloatField(default=0, verbose_name='Распределение')),
                ('gold', models.FloatField(blank=True, null=True, verbose_name='Золото')),
                ('silver', models.FloatField(blank=True, null=True, verbose_name='Серебро')),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.card', verbose_name='Карта')),
            ],
            options={
                'verbose_name': '(Карты) (Сундук) Элемент набора',
                'verbose_name_plural': '(Карты) (Сундук) Элементы набора',
                'db_table': 'drops',
            },
        ),
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': '(Карта) Стихия',
                'verbose_name_plural': '(Карты) Стихии',
                'db_table': 'elements',
            },
        ),
        migrations.CreateModel(
            name='Guild',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Наименование')),
                ('max_count_players', models.PositiveIntegerField(default=50, verbose_name='Максимальное количество игроков')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('icon', models.CharField(blank=True, max_length=255, null=True, verbose_name='Иконка')),
                ('type', models.BooleanField(default=True, verbose_name='Открытая гильдия')),
                ('tag', models.CharField(blank=True, max_length=9, null=True, unique=True, verbose_name='Тэг')),
                ('threshold', models.PositiveIntegerField(default=0, verbose_name='Ограничение')),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Дата создания')),
                ('date_delete', models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.country', verbose_name='Локация')),
            ],
            options={
                'verbose_name': 'Гильдия',
                'verbose_name_plural': '(Гильдия) Гильдии',
                'db_table': 'guilds',
            },
        ),
        migrations.CreateModel(
            name='GuildRank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_system', models.CharField(db_index=True, max_length=100, null=True, unique=True, verbose_name='Название звания (системное)')),
                ('name', models.CharField(max_length=100, null=True, unique=True, verbose_name='Название звания')),
                ('worth', models.IntegerField(default=0, null=True, unique=True, verbose_name='Значимость роли')),
                ('opportunity_accept_application', models.BooleanField(default=False, verbose_name='Может принимать/отклонять заявки')),
            ],
            options={
                'verbose_name': 'Звание в гильдии',
                'verbose_name_plural': '(Гильдия) Звания в гильдии',
                'db_table': 'guild_ranks',
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveIntegerField(null=True, unique=True, verbose_name='Уровень')),
                ('exp', models.PositiveIntegerField(default=1000, verbose_name='Опыт для следущего уровня')),
            ],
            options={
                'verbose_name': 'Уровень',
                'verbose_name_plural': 'Уровни',
                'db_table': 'levels',
            },
        ),
        migrations.CreateModel(
            name='PotionSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, unique=True, verbose_name='Размер')),
                ('system_name', models.CharField(db_index=True, max_length=100, null=True, unique=True, verbose_name='Системное название размера')),
            ],
            options={
                'verbose_name': '(Карта) (Зелье) Размер',
                'verbose_name_plural': '(Карты) (Зелья) Размеры',
                'db_table': 'potion_sizes',
            },
        ),
        migrations.CreateModel(
            name='Special',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Значение')),
                ('percentages', models.BooleanField(default=False, verbose_name='В процентах')),
                ('duration', models.IntegerField(default=0, help_text='Если < 0, то действует весь бой(кроме восстановления/понижения зворовья)', verbose_name='Длительность эффекта в раундах')),
            ],
            options={
                'verbose_name': '(Карта) (Эффекты) Эффект',
                'verbose_name_plural': '(Карты) (Эффекты) Эффекты',
                'db_table': 'specials',
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='Media ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, unique=True, verbose_name='Название объекта')),
                ('url', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ссылка на объект')),
            ],
            options={
                'verbose_name': 'Объект хранилища',
                'verbose_name_plural': 'Хранилище',
                'db_table': 'storage',
            },
        ),
        migrations.CreateModel(
            name='WeaponCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Название')),
                ('silver', models.PositiveIntegerField(default=0, verbose_name='Стоимость в серебре')),
                ('gold', models.PositiveIntegerField(default=0, verbose_name='Стоимость в золоте')),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Создано')),
                ('date_edited', models.DateTimeField(default=datetime.datetime.now, verbose_name='Изменено')),
                ('date_deleted', models.DateTimeField(blank=True, null=True, verbose_name='Удалено')),
                ('damage', models.PositiveIntegerField(default=1, verbose_name='Урон')),
                ('req_agility', models.PositiveIntegerField(default=1, verbose_name='Требуемая ловкость')),
                ('req_strength', models.PositiveIntegerField(default=1, verbose_name='Требуемая сила')),
                ('req_vitality', models.PositiveIntegerField(default=1, verbose_name='Требуемая живучесть')),
                ('critical_chance', models.FloatField(default=0.0, verbose_name='Шанс критического удара')),
                ('req_intelligence', models.PositiveIntegerField(default=1, verbose_name='Требуемы интеллект')),
                ('element', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.element', verbose_name='Стихия')),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storage', verbose_name='Иконка')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.cardtype', verbose_name='Вид карты')),
            ],
            options={
                'verbose_name': '(Карта) Оружия',
                'verbose_name_plural': '(Карты) Оружия',
                'db_table': 'weapon_cards',
            },
        ),
        migrations.CreateModel(
            name='WarriorCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Название')),
                ('silver', models.PositiveIntegerField(default=0, verbose_name='Стоимость в серебре')),
                ('gold', models.PositiveIntegerField(default=0, verbose_name='Стоимость в золоте')),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Создано')),
                ('date_edited', models.DateTimeField(default=datetime.datetime.now, verbose_name='Изменено')),
                ('date_deleted', models.DateTimeField(blank=True, null=True, verbose_name='Удалено')),
                ('level', models.PositiveIntegerField(default=1, verbose_name='Уровень')),
                ('experience', models.PositiveIntegerField(default=1, verbose_name='Опыт')),
                ('base', models.BooleanField(default=True, verbose_name='Магазинная')),
                ('defense', models.PositiveIntegerField(default=1, verbose_name='Защита')),
                ('agility', models.PositiveIntegerField(default=1, verbose_name='Ловкость')),
                ('volition', models.PositiveIntegerField(default=1, verbose_name='Воля')),
                ('strength', models.PositiveIntegerField(default=1, verbose_name='Сила')),
                ('vitality', models.PositiveIntegerField(default=1, verbose_name='Живучесть')),
                ('intelligence', models.PositiveIntegerField(default=1, verbose_name='Интеллект')),
                ('available_from', models.DateTimeField(blank=True, null=True, verbose_name='Достпуна от')),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storage', verbose_name='Иконка')),
                ('primary_element', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_element', to='core.element', verbose_name='Основная стихия')),
                ('secondary_element', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='secondary_element', to='core.element', verbose_name='Дополнительная стихия')),
                ('specials', models.ManyToManyField(blank=True, db_table='warrior_specials', to='core.Special', verbose_name='Особые эффекты')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.cardtype', verbose_name='Вид карты')),
            ],
            options={
                'verbose_name': '(Карта) Война',
                'verbose_name_plural': '(Карты) Войнов',
                'db_table': 'warrior_cards',
            },
        ),
        migrations.CreateModel(
            name='SpecialType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='Название')),
                ('system_name', models.CharField(db_index=True, max_length=255, verbose_name='Системное название')),
                ('to_enemy', models.BooleanField(default=False, verbose_name='Действует на противника')),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storage', verbose_name='Иконка')),
            ],
            options={
                'verbose_name': '(Карта) (Эффекты) Вид',
                'verbose_name_plural': '(Карты) (Эффекты) Виды',
                'db_table': 'special_types',
            },
        ),
        migrations.AddField(
            model_name='special',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.specialtype', verbose_name='Вид эффекта'),
        ),
        migrations.CreateModel(
            name='PotionCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Название')),
                ('silver', models.PositiveIntegerField(default=0, verbose_name='Стоимость в серебре')),
                ('gold', models.PositiveIntegerField(default=0, verbose_name='Стоимость в золоте')),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Создано')),
                ('date_edited', models.DateTimeField(default=datetime.datetime.now, verbose_name='Изменено')),
                ('date_deleted', models.DateTimeField(blank=True, null=True, verbose_name='Удалено')),
                ('level', models.PositiveIntegerField(default=1, verbose_name='Ранг зелья')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storage', verbose_name='Иконка')),
                ('size', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.potionsize', verbose_name='Размер')),
                ('specials', models.ManyToManyField(blank=True, db_table='potion_specials', to='core.Special', verbose_name='Особые эффекты')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.cardtype', verbose_name='Вид карты')),
            ],
            options={
                'verbose_name': '(Карта) Зелья',
                'verbose_name_plural': '(Карты) Зелий',
                'db_table': 'potion_cards',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('items', models.ManyToManyField(blank=True, db_table='item_items', to='core.Drop', verbose_name='Набор карт')),
            ],
            options={
                'verbose_name': '(Карты) (Сундук) Набор карт',
                'verbose_name_plural': '(Карты) (Сундук) Наборы карт',
                'db_table': 'items',
            },
        ),
        migrations.CreateModel(
            name='GuildPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Игрок в гильдии')),
                ('date_ban', models.DateTimeField(blank=True, null=True, verbose_name='Время до которого нельзя писать')),
                ('guild', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='players', to='core.guild', verbose_name='Гильдия')),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guild_player', to=settings.AUTH_USER_MODEL, verbose_name='Игрок')),
                ('rank', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.guildrank', verbose_name='Ранг игрока')),
            ],
            options={
                'verbose_name': 'Игрок гильдии',
                'verbose_name_plural': '(Гильдия) Игроки гильдии',
                'db_table': 'guild_players',
            },
        ),
        migrations.CreateModel(
            name='GuildApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('INVITATION', 'Invitation'), ('APPLICATION', 'Application')], max_length=100, null=True, verbose_name='Тип заявки')),
                ('status', models.CharField(choices=[('NEW', 'New'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('WITHDRAWN', 'Withdrawn')], max_length=100, null=True, verbose_name='Статус заявки')),
                ('date_create', models.DateTimeField(default=datetime.datetime.now, verbose_name='Дата создания')),
                ('date_change', models.DateTimeField(blank=True, null=True, verbose_name='Дата изменения')),
                ('date_delete', models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.guild', verbose_name='В какую гильдию')),
                ('whom', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Кого')),
            ],
            options={
                'verbose_name': 'Заявка в гильдию',
                'verbose_name_plural': '(Гильдия) Заявки в гильдию',
                'db_table': 'guild_applications',
            },
        ),
        migrations.CreateModel(
            name='Evolution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('req_agility', models.PositiveIntegerField(default=0, verbose_name='Требуемая ловкость')),
                ('req_strength', models.PositiveIntegerField(default=0, verbose_name='Требуемая сила')),
                ('req_vitality', models.PositiveIntegerField(default=0, verbose_name='Требуемая живучесть')),
                ('req_intelligence', models.PositiveIntegerField(default=0, verbose_name='Требуемый интеллект')),
                ('base_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='base_types', to='core.cardtype', verbose_name='Исходный подтип')),
                ('next_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='next_types', to='core.cardtype', verbose_name='Эволюционирует в')),
                ('specials', models.ManyToManyField(blank=True, db_table='evolution_specials', to='core.Special', verbose_name='Особые эффекты')),
            ],
            options={
                'verbose_name': '(Карта) (Воин) Эволюция',
                'verbose_name_plural': '(Карты) (Воины) Эволюции',
                'db_table': 'evolutions',
            },
        ),
        migrations.AddField(
            model_name='element',
            name='icon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storage', verbose_name='Иконка'),
        ),
        migrations.CreateModel(
            name='Chest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Название')),
                ('silver', models.PositiveIntegerField(default=0, verbose_name='Стоимость в серебре')),
                ('gold', models.PositiveIntegerField(default=0, verbose_name='Стоимость в золоте')),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Создано')),
                ('date_edited', models.DateTimeField(default=datetime.datetime.now, verbose_name='Изменено')),
                ('date_deleted', models.DateTimeField(blank=True, null=True, verbose_name='Удалено')),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storage', verbose_name='Иконка')),
                ('items', models.ManyToManyField(blank=True, db_table='chest_items', to='core.Item', verbose_name='Содержимое сундука')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.cardtype', verbose_name='Вид карты')),
            ],
            options={
                'verbose_name': '(Карта) Сундука',
                'verbose_name_plural': '(Карты) Сундуков',
                'db_table': 'chests',
            },
        ),
        migrations.AddField(
            model_name='cardtype',
            name='damage_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.damagetype', verbose_name='Вид урона'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='icon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storage', verbose_name='Иконка'),
        ),
        migrations.CreateModel(
            name='CardSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveIntegerField(default=1, verbose_name='Количество')),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.card', verbose_name='Карта')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to=settings.AUTH_USER_MODEL, verbose_name='Принадлежит')),
            ],
            options={
                'verbose_name': '(Пользователь) Карта',
                'verbose_name_plural': '(Пользователи) Карты',
                'db_table': 'card_sets',
            },
        ),
        migrations.CreateModel(
            name='ArmorCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Название')),
                ('silver', models.PositiveIntegerField(default=0, verbose_name='Стоимость в серебре')),
                ('gold', models.PositiveIntegerField(default=0, verbose_name='Стоимость в золоте')),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Создано')),
                ('date_edited', models.DateTimeField(default=datetime.datetime.now, verbose_name='Изменено')),
                ('date_deleted', models.DateTimeField(blank=True, null=True, verbose_name='Удалено')),
                ('req_agility', models.PositiveIntegerField(default=1, verbose_name='Требуемая ловкость')),
                ('req_strength', models.PositiveIntegerField(default=1, verbose_name='Требуемая сила')),
                ('req_vitality', models.PositiveIntegerField(default=1, verbose_name='Требуемая живучесть')),
                ('req_intelligence', models.PositiveIntegerField(default=1, verbose_name='Требуемый интеллект')),
                ('damage_reduction', models.PositiveIntegerField(default=1, verbose_name='Уменьшение урона')),
                ('element', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.element', verbose_name='Стихия')),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storage', verbose_name='Иконка')),
                ('specials', models.ManyToManyField(blank=True, db_table='armor_specials', to='core.Special', verbose_name='Особые эффекты')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.cardtype', verbose_name='Вид карты')),
            ],
            options={
                'verbose_name': '(Карта) Брони',
                'verbose_name_plural': '(Карты) Брони',
                'db_table': 'armor_cards',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.level', verbose_name='Уровень'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, db_table='user_permissions', help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission'),
        ),
    ]
