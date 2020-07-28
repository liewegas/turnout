# Generated by Django 2.2.14 on 2020-07-27 18:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('integration', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
