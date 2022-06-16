from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_add_progress_warriorcard'),
    ]

    operations = [
        migrations.RenameField(
            model_name='guild',
            old_name='date_delete',
            new_name='date_deleted',
        ),
        migrations.RenameField(
            model_name='guildapplication',
            old_name='date_delete',
            new_name='date_deleted',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='date_delete',
            new_name='date_deleted',
        ),
        migrations.RemoveField(
            model_name='armorcard',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='armorcard',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='chest',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='chest',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='guildapplication',
            name='date_change',
        ),
        migrations.RemoveField(
            model_name='guildapplication',
            name='date_create',
        ),
        migrations.RemoveField(
            model_name='potioncard',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='potioncard',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='warriorcard',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='warriorcard',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='weaponcard',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='weaponcard',
            name='currency',
        ),
        migrations.AddField(
            model_name='armorcard',
            name='amount_purchase',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='armorcard',
            name='amount_sale',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='armorcard',
            name='base',
            field=models.BooleanField(default=True, verbose_name='Магазинная'),
        ),
        migrations.AddField(
            model_name='armorcard',
            name='currency_purchase',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='armorcard_purchase', to='core.currency', verbose_name='Валюта покупки'),
        ),
        migrations.AddField(
            model_name='armorcard',
            name='currency_sale',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='armorcard_sale', to='core.currency', verbose_name='Валюта продажи'),
        ),
        migrations.AddField(
            model_name='cardset',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Создано'),
        ),
        migrations.AddField(
            model_name='cardset',
            name='date_deleted',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Удалено'),
        ),
        migrations.AddField(
            model_name='cardset',
            name='date_edited',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Изменено'),
        ),
        migrations.AddField(
            model_name='chest',
            name='amount_purchase',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='chest',
            name='amount_sale',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='chest',
            name='currency_purchase',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chest_purchase', to='core.currency', verbose_name='Валюта покупки'),
        ),
        migrations.AddField(
            model_name='chest',
            name='currency_sale',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chest_sale', to='core.currency', verbose_name='Валюта продажи'),
        ),
        migrations.AddField(
            model_name='guild',
            name='date_edited',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Изменено'),
        ),
        migrations.AddField(
            model_name='guildapplication',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания'),
        ),
        migrations.AddField(
            model_name='guildapplication',
            name='date_edited',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Дата изменения'),
        ),
        migrations.AddField(
            model_name='potioncard',
            name='amount_purchase',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='potioncard',
            name='amount_sale',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='potioncard',
            name='currency_purchase',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='potioncard_purchase', to='core.currency', verbose_name='Валюта покупки'),
        ),
        migrations.AddField(
            model_name='potioncard',
            name='currency_sale',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='potioncard_sale', to='core.currency', verbose_name='Валюта продажи'),
        ),
        migrations.AddField(
            model_name='warriorcard',
            name='amount_purchase',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='warriorcard',
            name='amount_sale',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='warriorcard',
            name='currency_purchase',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='warriorcard_purchase', to='core.currency', verbose_name='Валюта покупки'),
        ),
        migrations.AddField(
            model_name='warriorcard',
            name='currency_sale',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='warriorcard_sale', to='core.currency', verbose_name='Валюта продажи'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='amount_purchase',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='amount_sale',
            field=models.FloatField(null=True, verbose_name='Количество'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='base',
            field=models.BooleanField(default=True, verbose_name='Магазинная'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='currency_purchase',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weaponcard_purchase', to='core.currency', verbose_name='Валюта покупки'),
        ),
        migrations.AddField(
            model_name='weaponcard',
            name='currency_sale',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weaponcard_sale', to='core.currency', verbose_name='Валюта продажи'),
        ),
        migrations.AlterField(
            model_name='guild',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='date_departure',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата отправки'),
        ),
    ]
