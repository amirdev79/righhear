# Generated by Django 2.1.8 on 2019-04-24 08:20

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20190408_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrelations',
            name='meta_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, editable=False),
        ),
    ]
