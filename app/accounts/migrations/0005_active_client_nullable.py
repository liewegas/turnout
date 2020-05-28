# Generated by Django 2.2.12 on 2020-05-27 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_invite_foreign_keys'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='active_client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='active_client', to='multi_tenant.Client'),
        ),
    ]
