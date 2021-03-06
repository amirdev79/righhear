# Generated by Django 2.1 on 2019-01-20 11:19

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_userprofile_preferred_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacebookEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fb_id', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=10000)),
                ('name', models.CharField(max_length=100)),
                ('start_time', models.DateTimeField(editable=False)),
                ('end_time', models.DateTimeField(editable=False)),
                ('rsvp_status', models.CharField(max_length=20)),
                ('place', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fb_events', models.ManyToManyField(to='users.FacebookEvent')),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='fb_access_token',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='fb_id',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='userdata',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.UserProfile'),
        ),
    ]
