# Generated by Django 2.1.8 on 2019-04-08 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20190403_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermessage',
            name='email',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='usermessage',
            name='name',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='usermessage',
            name='phone',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
    ]
