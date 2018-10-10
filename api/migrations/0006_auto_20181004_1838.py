# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-10-04 23:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20181004_1648'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matchfile',
            old_name='match_acquired',
            new_name='match',
        ),
        migrations.AlterField(
            model_name='match',
            name='declined_motive',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='sale_detail',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='api.SaleDetail'),
        ),
    ]