# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-10-05 20:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20181005_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchfile',
            name='uploaded',
            field=models.IntegerField(choices=[(0, 'Loaded'), (1, 'Sent'), (2, 'Delivered'), (3, 'Read'), (4, 'Failed')], default=1),
        ),
    ]
