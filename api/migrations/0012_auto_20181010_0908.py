# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-10-10 14:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20181009_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='file_preview_url',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='match',
            name='file_url',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='payment',
            name='file_preview_url',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='payment',
            name='file_url',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='sale',
            name='file_preview_url',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='sale',
            name='file_url',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
