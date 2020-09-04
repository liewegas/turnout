# Generated by Django 2.2.16 on 2020-09-03 13:38

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0013_state_allow_print_and_forward'),
        ('integration', '0002_smalluuid_to_uuid'),
    ]

    operations = [
        migrations.CreateModel(
            name='MymoveLead',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mymove_created_at', models.DateTimeField(null=True)),
                ('first_name', models.TextField(null=True)),
                ('last_name', models.TextField(null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('move_date', models.DateTimeField(null=True)),
                ('new_address1', models.TextField(null=True)),
                ('new_address2', models.TextField(blank=True, null=True)),
                ('new_city', models.TextField(null=True)),
                ('new_zipcode', models.TextField(null=True, validators=[django.core.validators.RegexValidator('^[0-9]{5}$', 'Zip codes are 5 digits')])),
                ('new_zipcode_plus4', models.TextField(null=True)),
                ('new_housing_tenure', models.TextField(null=True)),
                ('old_address1', models.TextField(null=True)),
                ('old_address2', models.TextField(blank=True, null=True)),
                ('old_city', models.TextField(null=True)),
                ('old_zipcode', models.TextField(null=True, validators=[django.core.validators.RegexValidator('^[0-9]{5}$', 'Zip codes are 5 digits')])),
                ('old_zipcode_plus4', models.TextField(null=True)),
                ('old_housing_tenure', models.TextField(null=True)),
                ('actionnetwork_person_id', models.TextField(null=True)),
                ('new_state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='mymove_lead_new', to='election.State')),
                ('old_state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='mymove_lead_old', to='election.State')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]