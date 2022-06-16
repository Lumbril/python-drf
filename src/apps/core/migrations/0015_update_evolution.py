from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_add_user_auctionlot'),
    ]

    operations = [
        migrations.AddField(
            model_name='evolution',
            name='delta_agility',
            field=models.IntegerField(default=0, verbose_name='Изменение ловкости'),
        ),
        migrations.AddField(
            model_name='evolution',
            name='delta_defense',
            field=models.IntegerField(default=0, verbose_name='Изменение защиты'),
        ),
        migrations.AddField(
            model_name='evolution',
            name='delta_intelligence',
            field=models.IntegerField(default=0, verbose_name='Изменение интеллекта'),
        ),
        migrations.AddField(
            model_name='evolution',
            name='delta_strength',
            field=models.IntegerField(default=0, verbose_name='Изменение силы'),
        ),
        migrations.AddField(
            model_name='evolution',
            name='delta_vitality',
            field=models.IntegerField(default=0, verbose_name='Изменение живучести'),
        ),
        migrations.AddField(
            model_name='evolution',
            name='req_defense',
            field=models.PositiveIntegerField(default=0, verbose_name='Требуемый защиты'),
        ),
    ]
