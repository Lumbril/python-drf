from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_ticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='armorcard',
            name='ability_cooldown',
            field=models.PositiveIntegerField(default=3, verbose_name='Перезарядка способности в раундах'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='ability_cooldown',
            field=models.PositiveIntegerField(default=3, verbose_name='Перезарядка способности в раундах'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='attack_immediately',
            field=models.BooleanField(default=False, verbose_name='Атака сразу'),
        ),
        migrations.AlterField(
            model_name='warriorcard',
            name='specials',
            field=models.ManyToManyField(db_table='warrior_specials', to='core.Special', verbose_name='Особые эффекты'),
        ),
    ]
