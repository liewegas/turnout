# Generated by Django 2.2.12 on 2020-05-08 21:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('official', '0001_initial'),
        ('absentee', '0007_ballotrequest_state_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbsenteeLeoEmailOverride',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('region', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='official.Region')),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
