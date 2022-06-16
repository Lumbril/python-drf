from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_add_ability_card'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='armorcard',
            options={'verbose_name': '(Карта) Броня', 'verbose_name_plural': '(Карты) Брони'},
        ),
        migrations.AlterModelOptions(
            name='cardset',
            options={'verbose_name': '(Пользователь) Карта', 'verbose_name_plural': '(Пользователь) Карты'},
        ),
        migrations.AlterModelOptions(
            name='chest',
            options={'verbose_name': '(Карта) Сундук', 'verbose_name_plural': '(Карты) Сундуки'},
        ),
        migrations.AlterModelOptions(
            name='damagetype',
            options={'verbose_name': '(Карта) (Оружие) Вид урона', 'verbose_name_plural': '(Карты) (Оружия) Виды урона'},
        ),
        migrations.AlterModelOptions(
            name='drop',
            options={'verbose_name': '(Карты) (Сундук) Элемент набора', 'verbose_name_plural': '(Карты) (Сундуки) Элементы набора'},
        ),
        migrations.AlterModelOptions(
            name='guildapplication',
            options={'verbose_name': 'Заявка', 'verbose_name_plural': '(Гильдия) Заявки'},
        ),
        migrations.AlterModelOptions(
            name='guildplayer',
            options={'verbose_name': 'Игрок', 'verbose_name_plural': '(Гильдия) Игроки'},
        ),
        migrations.AlterModelOptions(
            name='guildrank',
            options={'verbose_name': 'Звание', 'verbose_name_plural': '(Гильдия) Звания'},
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'verbose_name': '(Карты) (Сундук) Набор карт', 'verbose_name_plural': '(Карты) (Сундуки) Наборы карт'},
        ),
        migrations.AlterModelOptions(
            name='potioncard',
            options={'verbose_name': '(Карта) Зелье', 'verbose_name_plural': '(Карты) Зелья'},
        ),
        migrations.AlterModelOptions(
            name='special',
            options={'verbose_name': '(Карта) (Эффект) Эффект', 'verbose_name_plural': '(Карты) (Эффекты) Эффекты'},
        ),
        migrations.AlterModelOptions(
            name='specialtype',
            options={'verbose_name': '(Карта) (Эффект) Вид', 'verbose_name_plural': '(Карты) (Эффекты) Виды'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': '(Пользователь) Пользователи'},
        ),
        migrations.AlterModelOptions(
            name='warriorcard',
            options={'verbose_name': '(Карта) Воин', 'verbose_name_plural': '(Карты) Воины'},
        ),
        migrations.AlterModelOptions(
            name='weaponcard',
            options={'verbose_name': '(Карта) Оружие', 'verbose_name_plural': '(Карты) Оружия'},
        ),
        migrations.AddField(
            model_name='card',
            name='total_power',
            field=models.PositiveIntegerField(default=0, verbose_name='Вес карты'),
        ),
    ]
