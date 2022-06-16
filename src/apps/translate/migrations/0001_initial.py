from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbreviation', models.CharField(db_index=True, max_length=10, null=True, unique=True, verbose_name='Сокращенное название')),
                ('title', models.CharField(max_length=100, null=True, unique=True, verbose_name='Полное название')),
            ],
            options={
                'verbose_name': 'Язык',
                'verbose_name_plural': 'Языки',
                'db_table': 'languages',
            },
        ),
        migrations.CreateModel(
            name='Translate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_translate', models.TextField(null=True, verbose_name='Ключ перевода')),
                ('translate', models.TextField(null=True, unique=True, verbose_name='Перевод')),
                ('language', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='translate.language', verbose_name='Язык')),
            ],
            options={
                'verbose_name': 'Перевод',
                'verbose_name_plural': 'Переводы',
                'db_table': 'translates',
            },
        ),
    ]
