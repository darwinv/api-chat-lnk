# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-29 21:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20180129_1541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alert',
            name='category',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='role',
        ),
        migrations.RemoveField(
            model_name='alertcategory',
            name='interval',
        ),
        migrations.RemoveField(
            model_name='contractcategory',
            name='category',
        ),
        migrations.RemoveField(
            model_name='creditcard',
            name='client',
        ),
        migrations.RemoveField(
            model_name='culqipayment',
            name='credit_cartd',
        ),
        migrations.RemoveField(
            model_name='declinedmotive',
            name='query_id',
        ),
        migrations.RemoveField(
            model_name='declinedmotive',
            name='specialist_id',
        ),
        migrations.RemoveField(
            model_name='fee',
            name='payment_type',
        ),
        migrations.RemoveField(
            model_name='fee',
            name='purchase',
        ),
        migrations.RemoveField(
            model_name='product',
            name='plan',
        ),
        migrations.RemoveField(
            model_name='product',
            name='seller',
        ),
        migrations.RemoveField(
            model_name='productssellernobillable',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productssellernobillable',
            name='seller',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='client',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='product',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='promotion',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='seller',
        ),
        migrations.DeleteModel(
            name='Quota',
        ),
        migrations.RemoveField(
            model_name='specialistcontract',
            name='client',
        ),
        migrations.RemoveField(
            model_name='specialistcontract',
            name='specialist',
        ),
        migrations.DeleteModel(
            name='TransactionCode',
        ),
        migrations.DeleteModel(
            name='Alert',
        ),
        migrations.DeleteModel(
            name='AlertCategory',
        ),
        migrations.DeleteModel(
            name='ContractCategory',
        ),
        migrations.DeleteModel(
            name='CreditCard',
        ),
        migrations.DeleteModel(
            name='CulqiPayment',
        ),
        migrations.DeleteModel(
            name='DeclinedMotive',
        ),
        migrations.DeleteModel(
            name='Fee',
        ),
        migrations.DeleteModel(
            name='Interval',
        ),
        migrations.DeleteModel(
            name='Plan',
        ),
        migrations.DeleteModel(
            name='Product',
        ),
        migrations.DeleteModel(
            name='ProductsSellerNoBillable',
        ),
        migrations.DeleteModel(
            name='Promotion',
        ),
        migrations.DeleteModel(
            name='Purchase',
        ),
        migrations.DeleteModel(
            name='SpecialistContract',
        ),
    ]