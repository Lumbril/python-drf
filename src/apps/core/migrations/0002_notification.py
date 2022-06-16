import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=100, null=True, verbose_name='Заголовок')),
                ('body', models.TextField(null=True, verbose_name='Содержание')),
                ('author', models.CharField(max_length=100, null=True, verbose_name='Кто отправил')),
                ('date_departure', models.DateTimeField(default=datetime.datetime.now, verbose_name='Дата отправки')),
                ('date_reading', models.DateTimeField(blank=True, null=True, verbose_name='Дата прочтения')),
                ('date_delete', models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Уведомление',
                'verbose_name_plural': 'Уведомления',
                'db_table': 'notifications',
            },
        ),
    ]
