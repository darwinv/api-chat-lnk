"""Serializer de Venta"""
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from api.models import Payment, MonthlyFee
from api.utils.tools import get_date_by_time
from datetime import datetime, date
from api.emails import BasicEmailAmazon
from dateutil.relativedelta import relativedelta


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer del pago."""

    monthly_fee = serializers.PrimaryKeyRelatedField(
        queryset=MonthlyFee.objects.all(), required=True)

    class Meta:
        """Modelo."""

        model = Payment
        fields = (
            'amount', 'operation_number', 'monthly_fee', 'payment_type',
            'observations', 'bank', 'id')
