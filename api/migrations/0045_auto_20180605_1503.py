# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-06-05 20:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0044_specialistdecline'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SpecialistDecline',
            new_name='Declinator',
        ),
    ]
