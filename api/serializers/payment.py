"""Serializer de Venta"""
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from api.models import Payment, MonthlyFee, Sale, SaleDetail
from api.models import QueryPlansAcquired, SellerContact
from api.utils.tools import get_date_by_time
from api.utils.querysets import get_next_fee_to_pay
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

    def create(self, validated_data):
        """Metodo para confirmar pago."""
        fee = MonthlyFee.objects.get(pk=validated_data["monthly_fee"])
        # valido que el monto confirmado es exacto
        if float(fee.fee_amount) == float(validated_data["amount"]):
            # cambio el estatus de la cuota a pago
            # 2 PAID
            fee.status = 2
            fee.save()
            # buscar contacto efectivo para acualitzar estado a efectivo cliente
            # filtar por el correo del id del cliente
            SellerContact.objects.filter(
                email=fee.sale.client.username).update(status=3)
            # compruebo si no hay mas cuotas pendientes por pagar
            if MonthlyFee.objects.filter(sale=fee.sale, status=1).exists():
                # cambio el estatus de la ventas
                # 2 Progreso
                Sale.objects.filter(pk=fee.sale_id).update(status=2)
            else:
                # 3 pagada
                Sale.objects.filter(pk=fee.sale_id).update(status=3)
            qsetdetail = SaleDetail.objects.filter(sale=fee.sale)

            # debo chequear si es por cuotas o no
            if fee.sale.is_fee:
                for detail in qsetdetail:
                    qacd = QueryPlansAcquired.objects.get(sale_detail=detail)
                    # libero el numero de consultas que corresponde
                    qacd.available_queries = qacd.query_plans.query_quantity / qacd.query_plans.validity_months
                    # actualizo cuantas consultas faltan por pagar
                    qacd.queries_to_pay = qacd.query_plans.query_quantity - qacd.available_queries
            else:
                pass

            data = {'qset': qsetdetail}

            mail = BasicEmailAmazon(
                subject="Confirmación de pago. Productos comprados",
                to=fee.sale.client.username, template='email/pin_code')

            mail.sendmail(args=data)
            validated_data["status"] = 2
            instance = Payment(**validated_data)
            instance.save()


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

class FeeSerializer(serializers.ModelSerializer):
    """Serializer del pago."""

    class Meta:
        """Modelo."""

        model = MonthlyFee
        fields = (
            'fee_amount', 'fee_order_number', 'fee_quantity', 'pay_before',
            'status', 'id')

class PaymentSaleDetailSerializer(serializers.ModelSerializer):
    """Serializer del pago."""
    attribute_product = serializers.SerializerMethodField()
    product_type_name = serializers.SerializerMethodField()
    class Meta:
        """Modelo."""

        model = SaleDetail
        fields = (
            'price', 'description', 'discount', 'pin_code', 'is_billable',
            'contract','product_type', 'sale', 'attribute_product',
            'product_type_name')

    def get_attribute_product(self, obj):
        """Devuelve client."""

        if obj.product_type.id == 1:
            plan = QueryPlansAcquired.objects.get(sale_detail=obj.id)
            sale = QueryPlansAcquiredSerializer(plan)
            return sale.data
        else:
            return None

    def get_product_type_name(self, obj):
        """Devuelve product_type."""
        return _(str(obj.product_type))

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

class SaleContactoDetailSerializer(serializers.ModelSerializer):
    """Serializer del pago."""

    products = serializers.SerializerMethodField()
    fee = serializers.SerializerMethodField()
    class Meta:
        """Modelo."""

        model = Sale
        fields = (
            'created_at', 'total_amount', 'reference_number', 'is_fee', 'id',
            'products', 'fee')


    def get_products(self, obj):
        """Devuelve sale detail."""
        sale_detail = SaleDetail.objects.filter(sale=obj.id)
        serializer = PaymentSaleDetailSerializer(sale_detail, many=True)
        return serializer.data

    def get_fee(self, obj):
        """Devuelve sale detail."""
        fee = get_next_fee_to_pay(obj.id)
        serializer = FeeSerializer(fee)
        return serializer.data
