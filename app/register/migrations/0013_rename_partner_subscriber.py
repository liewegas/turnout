# Generated by Django 2.2.12 on 2020-05-24 22:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('multi_tenant', '0012_rename_partner_subscriber'),
        ('register', '0012_registration_referring_tool'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='partner',
            field=models.ForeignKey(db_column='partner_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='multi_tenant.Client'),
        ),
        migrations.RenameField('Registration', 'partner', 'subscriber'),
        migrations.AlterField(
            model_name='registration',
            name='sms_opt_in_partner',
            field=models.BooleanField(db_column='sms_opt_in_partner', default=False, null=True),
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='sms_opt_in_partner',
            new_name='sms_opt_in_subscriber',
        ),
    ]
