from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_add_total_power_card'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guildapplication',
            name='to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applications', to='core.guild', verbose_name='В какую гильдию'),
        ),
    ]
