# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-04 19:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20171201_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='key',
            field=models.CharField(blank=True, max_length=45, null=True),
        ),
    ]