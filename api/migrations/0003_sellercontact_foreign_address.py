# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-08-17 19:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_api_store_procedure'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellercontact',
            name='foreign_address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]