# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-20 17:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_api_store_procedure'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellercontact',
            name='other_objection',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]