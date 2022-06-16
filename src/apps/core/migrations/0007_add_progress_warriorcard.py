from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_currency_add_system_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='warriorcard',
            name='progress',
            field=models.FloatField(default=0, verbose_name='Прогресс'),
        ),
    ]
