from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_drop_relation_currency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='potioncard',
            name='description',
        ),
        migrations.AddField(
            model_name='cardtype',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
    ]
