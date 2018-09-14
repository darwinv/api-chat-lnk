# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-09-14 19:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_merge_20180907_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterseller',
            name='number_year',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sellernonbillableplans',
            name='number_year',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
