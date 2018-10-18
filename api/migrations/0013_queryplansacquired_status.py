# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-10-10 16:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20181010_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='queryplansacquired',
            name='status',
            field=models.PositiveIntegerField(choices=[(1, 'Reserved'), (2, 'Pending Confirmation'), (3, 'Insert Your Pin'), (4, 'In Use'), (5, 'Culminated')], default=1),
        ),
    ]