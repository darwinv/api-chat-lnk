# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-28 15:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20171128_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='commercial_reason',
            field=models.CharField(max_length=45, null=True),
        ),
    ]
