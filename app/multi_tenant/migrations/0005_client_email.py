# Generated by Django 2.2.11 on 2020-03-31 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multi_tenant', '0004_inviteassociation'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='email',
            field=models.EmailField(default='turnout@localhost.local', max_length=254, null=True),
        ),
    ]