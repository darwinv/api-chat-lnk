# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-09-04 19:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_parameterseller'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterseller',
            name='people_purchase_goal',
            field=models.PositiveIntegerField(default=8),
            preserve_default=False,
        ),
    ]