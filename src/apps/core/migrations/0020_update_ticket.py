from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_add_specials_weaponcard'),
    ]

    operations = [
        migrations.AddField(
            model_name='cardtype',
            name='system_name',
            field=models.CharField(db_index=True, max_length=255, null=True, unique=True, verbose_name='Системное название'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='base',
            field=models.BooleanField(default=True, verbose_name='Магазинная'),
        ),
        migrations.AddField(
            model_name='user',
            name='enter_ticket',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to='core.ticket', verbose_name='Входной билет'),
        ),
        migrations.CreateModel(
            name='TicketCurrency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(null=True, verbose_name='Количество')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.currency', verbose_name='Валюта')),
            ],
            options={
                'verbose_name': '(Карта) (Билет) Валюта',
                'verbose_name_plural': '(Карты) (Билеты) Валюты',
                'db_table': 'currencies_tickets',
            },
        ),
        migrations.CreateModel(
            name='TicketCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(null=True, verbose_name='Количество')),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.card', verbose_name='Карта')),
            ],
            options={
                'verbose_name': '(Карта) (Билет) Карта',
                'verbose_name_plural': '(Карты) (Билеты) Карты',
                'db_table': 'cards_tickets',
            },
        ),
        migrations.AddField(
            model_name='ticket',
            name='cards',
            field=models.ManyToManyField(db_table='ticket_cards', to='core.TicketCard', verbose_name='Карты'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='currencies',
            field=models.ManyToManyField(db_table='ticket_currencies', to='core.TicketCurrency', verbose_name='Валюты'),
        ),
    ]
