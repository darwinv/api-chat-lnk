# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-13 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_merge_20180309_1023'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialistMessageList',
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
                'db_table': 'specialist_message_list',
            },
        ),
        migrations.AlterField(
            model_name='matchacquiredfiles',
            name='type_file',
            field=models.CharField(choices=[('1', 'Image'), ('2', 'Voice'), ('3', 'Document')], max_length=1),
        ),
        migrations.AlterField(
            model_name='message',
            name='content_type',
            field=models.CharField(choices=[('0', 'Text'), ('1', 'Image'), ('2', 'Video'), ('3', 'Voice'), ('4', 'Document')], max_length=1),
        ),
    ]
