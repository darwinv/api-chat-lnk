# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-28 19:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_auto_20180228_1442'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='reference',
            new_name='message_reference',
        ),
    ]
