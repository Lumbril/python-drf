import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BattleLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.UUIDField(blank=True, null=True, verbose_name='Временный ключ матча')),
                ('user1_data', models.TextField(null=True, verbose_name='Данные первого пользователя')),
                ('user2_data', models.TextField(null=True, verbose_name='Данные второго пользователя')),
                ('time', models.DateTimeField(default=datetime.datetime.now, verbose_name='Время')),
                ('user1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matches_user1', to=settings.AUTH_USER_MODEL, verbose_name='Первый пользователь')),
                ('user2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matches_user2', to=settings.AUTH_USER_MODEL, verbose_name='Второй пользователь')),
            ],
            options={
                'verbose_name': 'Матч',
                'verbose_name_plural': 'Матчи',
                'db_table': 'battle_logs',
            },
        ),
        migrations.CreateModel(
            name='BattleRound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.TextField(verbose_name='Данные раунда')),
                ('battle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rounds', to='battle.battlelog', verbose_name='Матч')),
            ],
            options={
                'verbose_name': 'Раунд',
                'verbose_name_plural': 'Раунды',
                'db_table': 'battle_rounds',
            },
        ),
    ]
