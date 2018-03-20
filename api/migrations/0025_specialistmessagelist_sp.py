# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-15 17:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_create_custom_index'),
        ('api', '0024_merge_20180307_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialistMessageList_sp',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('photo', models.CharField(blank=True, max_length=240)),
                ('nick', models.CharField(blank=True, max_length=40)),
                ('date', models.DateField(blank=True)),
                ('title', models.CharField(blank=True, max_length=240)),
                ('total', models.IntegerField(blank=True)),
                ('client', models.IntegerField(blank=True)),
                ('specialist', models.IntegerField(blank=True)),
            ],
            options={
                'managed': False,
            },
        ),
    ]
