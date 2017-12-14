# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-07 23:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_auto_20171207_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='status',
            field=models.CharField(choices=[('0', 'pending'), ('1', 'activated'), ('2', 'rejected'), ('3', 'deactivated')], default=1, max_length=1),
            preserve_default=False,
        ),
    ]