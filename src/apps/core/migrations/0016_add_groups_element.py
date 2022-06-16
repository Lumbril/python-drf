from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_update_evolution'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='groups',
            field=models.CharField(max_length=255, null=True, verbose_name='Принадлежность'),
        ),
    ]
