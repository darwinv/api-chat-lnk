# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-23 16:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='calification',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]