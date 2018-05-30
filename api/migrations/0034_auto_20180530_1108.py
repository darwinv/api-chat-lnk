# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-30 16:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_auto_20180529_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='ocupation',
            field=models.CharField(choices=[(1, 'Employer'), (2, 'Independent worker'), (3, 'Employee'), (4, 'Worker'), (5, 'Worker in a family business'), (6, 'Home worker'), (7, 'Other')], max_length=1),
        ),
        migrations.AlterField(
            model_name='matchacquired',
            name='status',
            field=models.CharField(choices=[(1, 'Requested'), (2, 'Accepted'), (3, 'Declined')], max_length=1),
        ),
        migrations.AlterField(
            model_name='matchacquiredfiles',
            name='type_file',
            field=models.CharField(choices=[(2, 'Image'), (3, 'Voice'), (4, 'Document')], max_length=1),
        ),
        migrations.AlterField(
            model_name='matchacquiredlog',
            name='status',
            field=models.CharField(choices=[(1, 'Requested'), (2, 'Accepted'), (3, 'Declined')], max_length=1),
        ),
        migrations.AlterField(
            model_name='message',
            name='content_type',
            field=models.CharField(choices=[(1, 'Text'), (2, 'Image'), (3, 'Video'), (4, 'Voice'), (5, 'Document')], max_length=1),
        ),
        migrations.AlterField(
            model_name='monthlyfee',
            name='status',
            field=models.CharField(choices=[(1, 'Pending'), (2, 'Paid')], max_length=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[(1, 'Pending'), (2, 'Accepted'), (3, 'Declined')], max_length=1),
        ),
        migrations.AlterField(
            model_name='query',
            name='status',
            field=models.CharField(choices=[(1, 'Requested'), (2, 'Accepted'), (3, 'Answered'), (4, 'To score'), (5, 'Absolved')], max_length=1),
        ),
        migrations.AlterField(
            model_name='querylogs',
            name='status_log',
            field=models.CharField(choices=[(1, 'Requested'), (2, 'Accepted'), (3, 'Answered'), (4, 'To score'), (5, 'Absolved')], max_length=1),
        ),
        migrations.AlterField(
            model_name='sellercontactnoefective',
            name='document_type',
            field=models.CharField(choices=[(1, 'DNI'), (2, 'Passport'), (3, 'Foreign Card')], max_length=1),
        ),
        migrations.AlterField(
            model_name='sellercontactnoefective',
            name='ocupation',
            field=models.CharField(blank=True, choices=[(1, 'Employer'), (2, 'Independent worker'), (3, 'Employee'), (4, 'Worker'), (5, 'Worker in a family business'), (6, 'Home worker'), (7, 'Other')], max_length=1),
        ),
        migrations.AlterField(
            model_name='user',
            name='document_type',
            field=models.CharField(choices=[(1, 'DNI'), (2, 'Passport'), (3, 'Foreign Card')], max_length=1, verbose_name='type document'),
        ),
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.CharField(choices=[(1, 'Pending'), (2, 'Activate'), (3, 'Reject'), (4, 'Deactivated')], default='1', max_length=1),
        ),
    ]
