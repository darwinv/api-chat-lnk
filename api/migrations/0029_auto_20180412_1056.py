# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-12 15:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_auto_20180406_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='nick',
            field=models.CharField(blank=True, max_length=45, null=True, verbose_name='nick'),
        ),
    ]
