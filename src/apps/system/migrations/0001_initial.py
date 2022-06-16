from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тип',
                'verbose_name_plural': 'Типы',
                'db_table': 'types',
            },
        ),
        migrations.CreateModel(
            name='SystemInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255, null=True, verbose_name='Ключ')),
                ('text', models.TextField(blank=True, default='Изображение не найдено', null=True, verbose_name='Текст')),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storage', verbose_name='Ссылка на источник')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.type', verbose_name='Тип')),
            ],
            options={
                'verbose_name': 'Системная информация',
                'verbose_name_plural': 'Системная информация',
                'db_table': 'system_info',
                'unique_together': {('key', 'type')},
            },
        ),
    ]
