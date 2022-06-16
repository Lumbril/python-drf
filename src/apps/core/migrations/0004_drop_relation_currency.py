from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_currency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='drop',
            name='gold',
        ),
        migrations.RemoveField(
            model_name='drop',
            name='silver',
        ),
        migrations.AddField(
            model_name='drop',
            name='amount',
            field=models.FloatField(blank=True, null=True, verbose_name='Количество валюты'),
        ),
        migrations.AddField(
            model_name='drop',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.currency', verbose_name='Валюта'),
        ),
    ]
