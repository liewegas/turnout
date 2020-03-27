# Generated by Django 2.2.11 on 2020-03-24 15:59

import common.enums
from django.db import migrations, models
import django_smalluuid.models
import enumfields.fields
import storage.backends
import storage.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StorageItem',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('uuid', django_smalluuid.models.SmallUUIDField(default=django_smalluuid.models.UUIDDefault(), editable=False, primary_key=True, serialize=False, unique=True)),
                ('token', django_smalluuid.models.SmallUUIDField(default=django_smalluuid.models.UUIDDefault(), unique=True)),
                ('app', enumfields.fields.EnumField(enum=common.enums.FileType, max_length=10)),
                ('file', models.FileField(storage=storage.backends.HighValueStorage(), upload_to='')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('expires', models.DateTimeField(default=storage.models.storage_expire_date_time)),
                ('first_download', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
