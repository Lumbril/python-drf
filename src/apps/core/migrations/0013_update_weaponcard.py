from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auctionlot'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='system_name',
            field=models.CharField(db_index=True, max_length=50, null=True, unique=True, verbose_name='Системное название'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='ratio_agility',
            field=models.FloatField(default=1, verbose_name='Коэффициент ловкости'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='ratio_intelligence',
            field=models.FloatField(default=1, verbose_name='Коэффициент интеллекта'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='ratio_strength',
            field=models.FloatField(default=1, verbose_name='Коэффициент силы'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='ratio_vitality',
            field=models.FloatField(default=1, verbose_name='Коэффициент живучести'),
        ),
    ]
