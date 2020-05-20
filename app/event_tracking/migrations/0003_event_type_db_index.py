# Generated by Django 2.2.12 on 2020-05-19 15:43

import common.enums
import common.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event_tracking', '0002_enumchartotextfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=common.fields.TurnoutEnumField(db_index=True, enum=common.enums.EventType),
        ),
    ]