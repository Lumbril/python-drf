from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_cardtype_add_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='system_name',
            field=models.CharField(db_index=True, max_length=255, null=True, unique=True, verbose_name='Системное название'),
        ),
        migrations.AlterField(
            model_name='currency',
            name='name',
            field=models.CharField(db_index=True, max_length=255, null=True, unique=True, verbose_name='Читаемое название'),
        ),
    ]
