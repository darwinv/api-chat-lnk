"""Serializer de Venta"""
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from api.models import Payment, MonthlyFee, Sale, SaleDetail, Match
from api.models import QueryPlansAcquired, SellerContact, User, MatchProduct
from api.utils.tools import get_date_by_time
from api.utils.querysets import get_next_fee_to_pay
from datetime import datetime, date
from api.emails import BasicEmailAmazon
from dateutil.relativedelta import relativedelta
from rest_framework.validators import UniqueValidator
from api.serializers.actors import ClientSerializer
from api.serializers.plan import QueryPlansAcquiredSerializer
from api.serializers.fee import FeeSerializer
from api.utils.parameters import Params
import sys
from api import pyrebase
from api.serializers.sale import increment_reference


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

    def validate_amount(self, value):
        """Validacion de amount."""
        data = self.get_initial()
        mfee = MonthlyFee.objects.get(pk=data["monthly_fee"])
        # si el monto es menor que el pago, devuelvo un error
        if float(value) < float(mfee.fee_amount):
            raise serializers.ValidationError(
                'This field must not be lesser than the corresponding.')
        return value

    def create(self, validated_data):
        """Metodo para confirmar pago."""
        fee = validated_data["monthly_fee"]
        # cambio el estatus de la cuota a pago
        # 2 PAID
        fee.status = 2
        fee.save()

        qsetdetail = SaleDetail.objects.filter(sale=fee.sale)
        # devolver plan name, validity_months, y query quantity de los productos adquiridos
        # mostrarlos en  la data
        data = {'qset': qsetdetail}
        # envio codigo pin por correo
        if fee.sale.status == 1:
            mail = BasicEmailAmazon(
                subject="Confirmación de pago. Productos comprados",
                to=fee.sale.client.username, template='email/pin_code')
            if 'test' not in sys.argv:
                mail.sendmail(args=data)
        # buscar contacto efectivo para acualitzar estado a efectivo cliente
        # filtar por el correo del id del cliente
        SellerContact.objects.filter(
            email_exact=fee.sale.client.username).update(type_contact=3)
        # compruebo si no hay mas cuotas pendientes por pagar
        if MonthlyFee.objects.filter(sale=fee.sale, status=1).exists():
            # cambio el estatus de la ventas
            # 2 Progreso
            Sale.objects.filter(pk=fee.sale_id).update(status=2)
        else:
            # 3 pagada
            Sale.objects.filter(pk=fee.sale_id).update(status=3)

        for detail in qsetdetail:
            qacd = QueryPlansAcquired.objects.get(sale_detail=detail)
            qpclient = qacd.queryplansclient_set.get()
            # debo chequear si es por cuotas o no
            if fee.sale.is_fee:
                # libero el numero de consultas que corresponde
                qacd.available_queries = qacd.available_queries + (qacd.query_plans.query_quantity / qacd.query_plans.validity_months)
                # actualizo cuantas consultas faltan por pagar
                qacd.queries_to_pay = qacd.query_plans.query_quantity - qacd.available_queries
            else:
                # libero el numero de consultas que corresponde
                qacd.available_queries = qacd.query_plans.query_quantity
                # actualizo cuantas consultas faltan por pagar
                qacd.queries_to_pay = 0
            qacd.save()
            # actualizo a pyrebase si es el elegido
            if 'test' not in sys.argv:
                if qpclient.is_chosen:
                    pyrebase.chosen_plan(
                        fee.sale.client.id,
                        {"available_queries": qacd.available_queries})
        # cambio el codigo del usuario
        user = User.objects.get(pk=fee.sale.client_id)
        if fee.sale.client.type_client == 'b':
            user.code = Params.CODE_PREFIX["client"] + user.ruc
        else:
            user.code = Params.CODE_PREFIX["client"] + user.document_number
        user.save()
        validated_data["status"] = 2
        instance = Payment(**validated_data)
        instance.save()
        return instance


class PaymentMatchSerializer(serializers.ModelSerializer):
    """Serializer del Pago."""
    match = serializers.PrimaryKeyRelatedField(
            queryset=Match.objects.all(), required=True, write_only=True)

    operation_number = serializers.CharField(validators=[UniqueValidator(
        queryset=Payment.objects.all())], required=True)

    class Meta:
        """Modelo."""

        model = Payment
        fields = ('amount', 'operation_number', 'payment_type',
                  'observations', 'bank', 'id', 'match')

    def validate_amount(self, value):
        """Validacion de amount."""
        price = MatchProduct.objects.first().price
        # si el monto es menor que el pago, devuelvo un error
        if float(value) < float(price):
            raise serializers.ValidationError(
                'This field must not be lesser than the corresponding.')
        return value

    def create(self, validated_data):
        """Crear pago de especialista."""
        match = validated_data.pop('match')
        # import pdb; pdb.set_trace()
        match = Match.objects.get(pk=match.id)
        instance = Payment(**validated_data)
        instance.save()
        match.specialist_payment = instance
        client = match.client
        # se verifica si ya fue cliente el usuario que solicito el match
        # si ya lo fue pasa a status 5 directo sino pasa a 4. pendiente de pago
        is_client = Sale.objects.filter(saledetail__product_type=1,
                                        saledetail__is_billable=True,
                                        client=client,
                                        status__range=(2, 3)).exists()
        if is_client:
            match.status = 5
        else:            

            sale = Sale.objects.create(place="BCP", total_amount=match.price,
                                   reference_number=increment_reference(),
                                   description='pago de match',
                                   client=match.client, status=1)

            sale_detail = SaleDetail.objects.create(price=match.price,
                                                    description="Contratacion de especialista",
                                                    discount=float(0),
                                                    pin_code='XXXXXX',
                                                    is_billable=True,
                                                    product_type_id=2, sale=sale)
            match.status = 4
            match.sale_detail = sale_detail

        match.save()
        return instance


class PaymentMatchClientSerializer(serializers.ModelSerializer):
    """Se crea, venta, pago y cambia el match."""

    match = serializers.PrimaryKeyRelatedField(
            queryset=Match.objects.all(), required=True, write_only=True)

    class Meta:
        """Modelo."""

        model = Payment
        fields = ('amount', 'operation_number', 'payment_type',
                  'observations', 'bank', 'id', 'match')

    def validate_amount(self, value):
        """Validacion de amount."""
        price = MatchProduct.objects.first().price
        # si el monto es menor que el pago, devuelvo un error
        if float(value) < float(price):
            raise serializers.ValidationError(
                _('This field must not be lesser than the corresponding'))
        return value

    def create(self, validated_data):
        """Crear pago de especialista."""
        match = validated_data.pop('match')
        # import pdb; pdb.set_trace()
        match = Match.objects.get(pk=match.id)
        # import pdb; pdb.set_trace()       

        instance = Payment(**validated_data)
        instance.save()
        match.status = 5        
        match.save()
        return instance

class PaymentSaleSerializer(serializers.ModelSerializer):
    """Serializer del pago."""

    client__first_name = serializers.SerializerMethodField()
    client__last_name = serializers.SerializerMethodField()
    client__business_name = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    pay_before = serializers.SerializerMethodField()

    class Meta:
        """Modelo."""

        model = Sale
        fields = (
            'created_at', 'total_amount', 'reference_number', 'is_fee', 'id',
            'client__first_name','client__last_name', 'client__business_name', 'pay_before')

    def get_pay_before(self, obj):
        """Devuelve pay_before."""
        if type(obj) is dict:
            return str(obj['pay_before'])
        return None

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
            return obj['client__business_name']
        return obj.client.business_name



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
    created_at = serializers.SerializerMethodField()
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

    def get_created_at(self, obj):
        """Devuelve created_at."""
        if type(obj) is dict:
            return str(obj['created_at'])
        return str(obj.created_at)
