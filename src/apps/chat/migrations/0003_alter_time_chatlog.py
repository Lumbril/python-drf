from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatlog',
            name='time',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Время'),
        ),
    ]
