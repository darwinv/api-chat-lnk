# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-18 22:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_merge_20171018_1727'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quota',
            old_name='end',
            new_name='date',
        ),
        migrations.RemoveField(
            model_name='quota',
            name='start',
        ),
    ]
