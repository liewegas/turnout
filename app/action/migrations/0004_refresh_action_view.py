# Generated by Django 2.2.12 on 2020-05-19 18:19

import django.db.models.deletion
from django.db import migrations, models

from action.migrations import (
    ACTIONDETAIL_VIEW_CREATION_SQL,
    ACTIONDETAIL_VIEW_REVERSE_SQL,
)


class Migration(migrations.Migration):

    dependencies = [
        ("action", "0003_refresh_action_view"),
    ]

    operations = [
        migrations.RunSQL(ACTIONDETAIL_VIEW_CREATION_SQL),
    ]
