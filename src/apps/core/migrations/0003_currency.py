from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0002_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, null=True, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Валюта',
                'verbose_name_plural': 'Валюты',
                'db_table': 'currencies',
            },
        ),
        migrations.RemoveField(
            model_name='armorcard',
            name='gold',
        ),
        migrations.RemoveField(
            model_name='armorcard',
            name='silver',
        ),
        migrations.RemoveField(
            model_name='chest',
            name='gold',
        ),
        migrations.RemoveField(
            model_name='chest',
            name='silver',
        ),
        migrations.RemoveField(
            model_name='potioncard',
            name='gold',
        ),
        migrations.RemoveField(
            model_name='potioncard',
            name='silver',
        ),
        migrations.RemoveField(
            model_name='warriorcard',
            name='gold',
        ),
        migrations.RemoveField(
            model_name='warriorcard',
            name='silver',
        ),
        migrations.RemoveField(
            model_name='weaponcard',
            name='gold',
        ),
        migrations.RemoveField(
            model_name='weaponcard',
            name='silver',
        ),
        migrations.AddField(
            model_name='armorcard',
            name='amount',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='chest',
            name='amount',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='potioncard',
            name='amount',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='warriorcard',
            name='amount',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='amount',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, db_table='user_groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='groups', related_query_name='user', to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, db_table='user_permissions', help_text='Specific permissions for this user.', related_name='permissions', related_query_name='user', to='auth.Permission'),
        ),
        migrations.AddField(
            model_name='armorcard',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.currency', verbose_name='Валюта'),
        ),
        migrations.AddField(
            model_name='chest',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.currency', verbose_name='Валюта'),
        ),
        migrations.AddField(
            model_name='potioncard',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.currency', verbose_name='Валюта'),
        ),
        migrations.AddField(
            model_name='warriorcard',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.currency', verbose_name='Валюта'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.currency', verbose_name='Валюта'),
        ),
    ]
