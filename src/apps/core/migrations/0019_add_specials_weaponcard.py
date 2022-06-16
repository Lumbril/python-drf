from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_add_fields_cards'),
    ]

    operations = [
        migrations.AddField(
            model_name='weaponcard',
            name='specials',
            field=models.ManyToManyField(blank=True, db_table='weapon_specials', to='core.Special', verbose_name='Особые эффекты'),
        ),
    ]
