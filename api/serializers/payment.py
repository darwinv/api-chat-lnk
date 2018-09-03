"""Serializer de Venta"""
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from api.models import Payment, MonthlyFee, Sale, SaleDetail
from api.models import QueryPlansAcquired
from api.utils.tools import get_date_by_time
from datetime import datetime, date
from api.emails import BasicEmailAmazon
from dateutil.relativedelta import relativedelta
from rest_framework.validators import UniqueValidator
from api.serializers.actors import ClientSerializer
from api.serializers.plan import QueryPlansAcquiredSerializer

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

    client__first_name = serializers.SerializerMethodField()
    client__last_name = serializers.SerializerMethodField()
    client__business_name = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    class Meta:
        """Modelo."""

        model = Sale
        fields = (
            'created_at', 'total_amount', 'reference_number', 'is_fee', 'id',
            'client__first_name','client__last_name', 'client__business_name')

    def get_created_at(self, obj):
        """Devuelve created_at."""
        if type(obj) is dict:
            return str(obj['created_at'])
        return str(obj.created_at)

    def get_client__first_name(self, obj):
        """Devuelve client__first_name."""
        if type(obj) is dict:
            return str(obj['client__first_name'])
        return str(obj.client.first_name)

    def get_client__last_name(self, obj):
        """Devuelve client__last_name."""
        if type(obj) is dict:
            return str(obj['client__last_name'])
        return str(obj.client.last_name)

    def get_client__business_name(self, obj):
        """Devuelve client__business_name."""
        if type(obj) is dict:
            return str(obj['client__business_name'])
        return str(obj.client.business_name)


class PaymentSaleDetailSerializer(serializers.ModelSerializer):
    """Serializer del pago."""
    attribute_product = serializers.SerializerMethodField()

    class Meta:
        """Modelo."""

        model = SaleDetail
        fields = (
            'price', 'description', 'discount', 'pin_code', 'is_billable',
            'contract','product_type', 'sale', 'attribute_product')

    def get_attribute_product(self, obj):
        """Devuelve client."""
        
        if obj.product_type.id == 1:
            plan = QueryPlansAcquired.objects.get(sale_detail=obj.id)
            sale = QueryPlansAcquiredSerializer(plan)
            return sale.data
        else:
            return None

class SaleWithFeeSerializer(serializers.Serializer):
    """serializador para detalle de venta"""

    detail = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    def get_detail(self, obj):
        """Devuelve client."""
        sale = PaymentSaleSerializer(obj)
        return sale.data

    def get_products(self, obj):
        """Devuelve sale detail."""
        sale_detail = SaleDetail.objects.filter(sale=obj.id)
        serializer = PaymentSaleDetailSerializer(sale_detail, many=True)
        return serializer.data

class PaymentSalePendingDetailSerializer(serializers.ModelSerializer):
    """Serializer del pago."""

    client = serializers.SerializerMethodField()
    sale = serializers.SerializerMethodField()
    class Meta:
        """Modelo."""

        model = MonthlyFee
        fields = (
            'fee_amount', 'fee_order_number', 'fee_quantity', 'pay_before',
            'status', 'client', 'sale', 'id')

    def get_client(self, obj):
        """Devuelve client."""
        client = ClientSerializer(obj.sale.client)
        return client.data

    def get_sale(self, obj):
        """Devuelve sale."""
        
        serializer = SaleWithFeeSerializer(obj.sale)
        
        return serializer.data
