# Generated by Django 2.2.12 on 2020-04-14 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('verifier', '0010_remove_unnecessary_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lookup',
            name='sms_opt_in',
            field=models.BooleanField(default=None, blank=True, null=True),
        ),
    ]
