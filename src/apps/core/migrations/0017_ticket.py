import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_add_groups_element'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, verbose_name='Название')),
                ('amount_purchase', models.FloatField(null=True, verbose_name='Количество')),
                ('amount_sale', models.FloatField(null=True, verbose_name='Количество')),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Создано')),
                ('date_edited', models.DateTimeField(default=datetime.datetime.now, verbose_name='Изменено')),
                ('date_deleted', models.DateTimeField(blank=True, null=True, verbose_name='Удалено')),
                ('date_activation', models.DateTimeField(blank=True, null=True, verbose_name='Активировано')),
                ('currency_purchase', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ticket_purchase', to='core.currency', verbose_name='Валюта покупки')),
                ('currency_sale', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ticket_sale', to='core.currency', verbose_name='Валюта продажи')),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storage', verbose_name='Иконка')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.cardtype', verbose_name='Вид карты')),
            ],
            options={
                'verbose_name': '(Карта) Билет',
                'verbose_name_plural': '(Карты) Билеты',
                'db_table': 'tickets',
            },
        ),
    ]
