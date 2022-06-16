from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_update_ticket'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cardset',
            name='is_auction',
        ),
        migrations.AddField(
            model_name='armorcard',
            name='ability_name',
            field=models.CharField(max_length=255, null=True, verbose_name='Название способности'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='ability_name',
            field=models.CharField(default='null', max_length=255, verbose_name='Название способности'),
        ),
        migrations.AlterField(
            model_name='armorcard',
            name='ability_cooldown',
            field=models.PositiveIntegerField(default=3, verbose_name='Перезарядка способности в ходах'),
        ),
        migrations.AlterField(
            model_name='weaponcard',
            name='ability_cooldown',
            field=models.PositiveIntegerField(default=3, verbose_name='Перезарядка способности в ходах'),
        ),
    ]
