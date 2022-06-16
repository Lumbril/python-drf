from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_add_potential_warriorcard'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='date_edited',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Дата изменения'),
        ),
        migrations.AddField(
            model_name='notification',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='Прочитано'),
        ),
    ]
