# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-03 20:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_auto_20180622_1450'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='queryplansacquired',
            name='client',
        ),
    ]
