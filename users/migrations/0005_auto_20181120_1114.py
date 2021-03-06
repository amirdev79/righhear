# Generated by Django 2.1 on 2018-11-20 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20181120_1114'),
        ('users', '0004_auto_20181111_1359'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSwipeAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_time', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(choices=[('LEFT', 'LEFT'), ('UP', 'UP'), ('RIGHT', 'RIGHT'), ('DOWN', 'DOWN')], default='LEFT', max_length=6)),
                ('event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='events.Event')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.UserProfile')),
            ],
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='device_id',
            field=models.CharField(editable=False, max_length=50),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='last_login',
            field=models.DateTimeField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='model',
            field=models.CharField(blank=True, editable=False, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='os',
            field=models.CharField(blank=True, editable=False, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='os_version',
            field=models.CharField(blank=True, editable=False, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='push_token',
            field=models.CharField(blank=True, editable=False, max_length=256, unique=True),
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='timezone',
            field=models.CharField(blank=True, editable=False, max_length=50, null=True),
        ),
    ]
