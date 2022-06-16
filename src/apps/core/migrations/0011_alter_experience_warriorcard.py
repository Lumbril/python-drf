from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_add_is_read_notification'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='warriorcard',
            options={'verbose_name': '(Карта) Воина', 'verbose_name_plural': '(Карты) Воинов'},
        ),
        migrations.AlterField(
            model_name='warriorcard',
            name='experience',
            field=models.PositiveIntegerField(default=0, verbose_name='Опыт'),
        ),
    ]
