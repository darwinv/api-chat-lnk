# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-08-09 16:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20180802_0940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objection',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='queryplansclient',
            name='status',
            field=models.PositiveIntegerField(choices=[(1, 'Active'), (2, 'Deactivated')]),
        ),
        migrations.AlterField(
            model_name='queryplansmanage',
            name='status',
            field=models.PositiveIntegerField(choices=[(1, 'Active'), (2, 'Deactivated'), (3, 'Processing')]),
        ),
    ]
