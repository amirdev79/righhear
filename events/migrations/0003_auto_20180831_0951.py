# Generated by Django 2.1 on 2018-08-31 06:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20180830_0823'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='sub_category',
        ),
        migrations.AddField(
            model_name='artist',
            name='sub_categories',
            field=models.ManyToManyField(to='events.EventSubCategory'),
        ),
        migrations.AddField(
            model_name='event',
            name='sub_categories',
            field=models.ManyToManyField(to='events.EventSubCategory'),
        ),
        migrations.AlterField(
            model_name='event',
            name='artist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='events.Artist'),
        ),
    ]
