"""Serializer de Venta"""
from rest_framework import serializers
from api.models import MonthlyFee

class FeeSerializer(serializers.ModelSerializer):
    """Serializer del pago."""

    class Meta:
        """Modelo."""

        model = MonthlyFee
        fields = (
            'fee_amount', 'fee_order_number', 'fee_quantity', 'pay_before',
            'status', 'id')