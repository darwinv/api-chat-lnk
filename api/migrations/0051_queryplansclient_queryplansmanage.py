# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-05 17:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0050_remove_queryplansacquired_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryPlansClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.BooleanField(default=True)),
                ('transfer', models.BooleanField(default=True)),
                ('share', models.BooleanField(default=True)),
                ('empower', models.BooleanField(default=True)),
                ('status', models.PositiveIntegerField(choices=[(1, 'Active'), (2, 'Deactive')])),
                ('acquired_plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.QueryPlansAcquired')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.Client')),
            ],
        ),
        migrations.CreateModel(
            name='QueryPlansManage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_operation', models.PositiveIntegerField(choices=[(1, 'Transfer'), (2, 'Share'), (3, 'Empower')])),
                ('status', models.PositiveIntegerField(choices=[(1, 'Active'), (2, 'Deactive')])),
                ('acquired_plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='plan_acquired_plan', to='api.QueryPlansAcquired')),
                ('new_acquired_plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.QueryPlansAcquired')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.Client')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='plan_sender', to='api.Client')),
            ],
        ),
    ]
