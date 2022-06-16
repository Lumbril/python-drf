from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_experience_warriorcard'),
    ]

    operations = [
        migrations.AddField(
            model_name='cardset',
            name='is_auction',
            field=models.BooleanField(default=False, null=True, verbose_name='На аукционе'),
        ),
        migrations.CreateModel(
            name='AuctionLot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost', models.PositiveIntegerField(default=0, null=True, verbose_name='Стоимость')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Создано')),
                ('date_edited', models.DateTimeField(auto_now=True, null=True, verbose_name='Изменено')),
                ('date_deleted', models.DateTimeField(blank=True, null=True, verbose_name='Удалено')),
                ('currency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.currency', verbose_name='Валюта')),
                ('lot', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.cardset', verbose_name='Лот')),
            ],
            options={
                'verbose_name': 'Лот',
                'verbose_name_plural': 'Аукционные лоты',
                'db_table': 'auction_lots',
            },
        ),
    ]
