# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-20 22:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20180216_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='changed_on',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
