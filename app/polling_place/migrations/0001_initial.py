# Generated by Django 2.2.16 on 2020-09-15 14:26

import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('multi_tenant', '0020_enable_api_on_default'),
        ('election', '0014_state_allow_absentee_print_and_forward'),
        ('action', '0010_index_last_voter_lookup'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollingPlaceLookup',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('embed_url', models.TextField(blank=True, null=True)),
                ('utm_campaign', models.TextField(blank=True, null=True)),
                ('utm_source', models.TextField(blank=True, null=True)),
                ('utm_medium', models.TextField(blank=True, null=True)),
                ('utm_term', models.TextField(blank=True, null=True)),
                ('utm_content', models.TextField(blank=True, null=True)),
                ('session_id', models.UUIDField(blank=True, null=True)),
                ('source', models.TextField(blank=True, null=True)),
                ('email_referrer', models.TextField(blank=True, null=True)),
                ('mobile_referrer', models.TextField(blank=True, null=True)),
                ('sms_opt_in_subscriber', models.BooleanField(db_column='sms_opt_in_partner', default=False, null=True)),
                ('unstructured_address', models.TextField(null=True)),
                ('dnc_result', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('dnc_status', models.TextField(null=True)),
                ('civic_result', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('civic_status', models.TextField(null=True)),
                ('address1', models.TextField(blank=True, null=True)),
                ('address2', models.TextField(blank=True, null=True)),
                ('city', models.TextField(blank=True, null=True)),
                ('zipcode', models.TextField(blank=True, null=True, validators=[django.core.validators.RegexValidator('^[0-9]{5}$', 'Zip codes are 5 digits')])),
                ('action', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='action.Action')),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='election.State')),
                ('subscriber', models.ForeignKey(db_column='partner_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='multi_tenant.Client')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]