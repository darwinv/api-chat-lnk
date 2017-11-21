# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-15 22:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20171110_1843'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='commercial_group',
        ),
        migrations.AlterField(
            model_name='client',
            name='civil_state',
            field=models.CharField(choices=[('c', 'cohabiting'), ('e', 'separated'), ('m', 'married'), ('w', 'widower'), ('d', 'divorced'), ('s', 'single')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='ocupation',
            field=models.CharField(choices=[('0', 'Employer'), ('1', 'Independent worker'), ('2', 'Employee'), ('3', 'Worker'), ('4', 'Worker in a family business'), ('5', 'Home worker'), ('6', 'Other')], max_length=1),
        ),
        migrations.AlterField(
            model_name='client',
            name='profession',
            field=models.CharField(max_length=45, null=True),
        ),
        migrations.DeleteModel(
            name='CommercialGroup',
        ),
        migrations.DeleteModel(
            name='Profession',
        ),
    ]
