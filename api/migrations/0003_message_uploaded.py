# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-09-26 16:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_store_procedure'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='uploaded',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
