"""Serializer de Venta"""
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from api.models import Payment, MonthlyFee, Sale
from api.utils.tools import get_date_by_time
from datetime import datetime, date
from api.emails import BasicEmailAmazon
from dateutil.relativedelta import relativedelta
from rest_framework.validators import UniqueValidator


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer del pago."""

    monthly_fee = serializers.PrimaryKeyRelatedField(
        queryset=MonthlyFee.objects.all(), required=True)

    operation_number = serializers.CharField(validators=[UniqueValidator(
        queryset=Payment.objects.all())], required=True)

    class Meta:
        """Modelo."""

        model = Payment
        fields = (
            'amount', 'operation_number', 'monthly_fee', 'payment_type',
            'observations', 'bank', 'id')

class PaymentSaleSerializer(serializers.ModelSerializer):
    """Serializer del pago."""

    client__first_name = serializers.CharField(read_only=True)
    client__last_name = serializers.CharField(read_only=True)

    class Meta:
        """Modelo."""

        model = Sale
        fields = (
            'created_at', 'total_amount', 'reference_number', 'is_fee', 'id',
            'client__first_name','client__last_name', 'client__business_name')
