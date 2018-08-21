"""Serializer de Venta"""
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from api.models import Payment
from api.utils.tools import get_date_by_time
from datetime import datetime, date
from api.emails import BasicEmailAmazon
from dateutil.relativedelta import relativedelta


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer del pago."""

    class Meta:
        """Modelo."""

        model = Payment
        fields = (
            'amount', 'operation_number', 'monthly_fee', 'payment_type',
            'observations')
