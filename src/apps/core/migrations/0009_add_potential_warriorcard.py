from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_sale_purchase_card'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warriorcard',
            name='volition',
        ),
        migrations.AddField(
            model_name='warriorcard',
            name='potential',
            field=models.PositiveIntegerField(default=1, verbose_name='Потенциал'),
        ),
    ]
