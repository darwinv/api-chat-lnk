# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-08-20 20:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_sellercontact_foreign_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='account_number_drawer',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='agency_code',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='check_number',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='credit_card_cvc',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='credit_cart_number',
        ),
    ]