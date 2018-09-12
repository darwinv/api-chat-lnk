"""Serializer de Venta"""
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from api.models import QueryPlansAcquired, QueryPlansClient, MonthlyFee
from api.models import QueryPlans, Client, Seller, ProductType
from api.models import SellerNonBillablePlans, Sale, SaleDetail
from api.utils.tools import get_date_by_time
from datetime import datetime, date
from api.emails import BasicEmailAmazon
from dateutil.relativedelta import relativedelta
import random
import string

hoy = date.today()


def increment_reference():
    """Campo autoincremental de numero de referencia."""
    last_invoice = Sale.objects.all().order_by('id').last()
    if not last_invoice:
        return 'CD0001'
    invoice_no = last_invoice.reference_number
    invoice_int = int(invoice_no.split('CD')[-1])
    new_invoice_int = invoice_int + 1
    new_invoice_no = 'CD' + str(new_invoice_int)
    return new_invoice_no


def generate_pin_code():
    """Genera el codigo Pin."""
    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return code


class ProductSerializer(serializers.Serializer):
    """Serializer para compra de producto."""

    product_type = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(), required=True)
    is_billable = serializers.BooleanField()
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=QueryPlans.objects.all(), required=False)
    quantity = serializers.IntegerField(max_value=99, min_value=1)

    def validate(self, data):
        """Validar producto."""
        plan = data["plan_id"]
        client = self.context["client"]
        hoy.month
        if data['is_billable'] is False:
            # import pdb; pdb.set_trace()
            detail = SaleDetail.objects.filter(sale__client_id=client)
            if detail.filter(is_billable=False).exists():
                raise serializers.ValidationError(
                    _("client can no longer be given promotional plans"))
            if 'seller' in self.context:
                seller = self.context["seller"]
                try:
                    obj = SellerNonBillablePlans.objects.get(
                        query_plans=plan, seller_id=seller,
                        number_month=hoy.month)
                    if obj.quantity < 1:
                        raise serializers.ValidationError(
                            _("seller exceeds quantity for this promotional plan"))
                except SellerNonBillablePlans.DoesNotExist:
                    raise serializers.ValidationError(
                        _("this is not a promotional plan for this seller"))
        return data


class SaleSerializer(serializers.Serializer):
    """Serializer de venta."""
    # vendedor es  opcional, ya que puede comprar el cliente por su cuenta
    seller = serializers.PrimaryKeyRelatedField(queryset=Seller.objects.all(),
                                                required=False)
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(),
                                                required=True)
    # listado de  productos que se agregaran en la venta
    products = serializers.ListField(child=ProductSerializer(), required=True)
    is_fee = serializers.BooleanField(required=True)
    place = serializers.CharField(allow_blank=True)
    description = serializers.CharField(required=False)
    reference_number = serializers.CharField(default=increment_reference)

    def to_representation(self, instance):
        return {"id": instance.id,
                "reference_number": instance.reference_number,
                "total_amount": instance.total_amount,
                "fees": instance.monthlyfee_set.all().count(),
                }

    def create(self, validated_data):
        """Metodo para guardar en venta."""
        products = validated_data.pop("products")
        total_amount = self.get_total_amount(products)
        validated_data["total_amount"] = total_amount
        instance = Sale(**validated_data)
        instance.save()
        sale_detail = {}
        for product in products:
            # Crear cuotas
            if validated_data["is_fee"]:
                n_fees = product["plan_id"].validity_months
                fee_amount = float((product["plan_id"].price * product["quantity"])/n_fees )
            else:
                n_fees = 1
                fee_amount = float(product["plan_id"].price)

            for i in range(1, n_fees+1):
                pay_day = date.today() + relativedelta(days=3) # Hardcoded cambiar la cantidad de dias
                sale_id = instance
                
                MonthlyFee.objects.create(fee_amount=fee_amount,
                                          fee_order_number=i, status=1,
                                          sale=sale_id,
                                          pay_before=pay_day,
                                          fee_quantity=n_fees)

            plan_acquired = {}
            for prx in range(product["quantity"]):
                # verificamos si el producto es plan de consultass
                if product["product_type"].id == 1:
                    sale_detail["pin_code"] = generate_pin_code()
                    sale_detail["description"] = product["product_type"].description
                    sale_detail["price"] = float(product["plan_id"].price)
                    sale_detail["is_billable"] = product["is_billable"]
                    # comparo si es promocional o no
                    if product["is_billable"]:
                        sale_detail["discount"] = 0.0
                        plan_acquired["is_active"] = False
                    else:
                        validated_data["is_fee"] = False
                        # se activa automaticamente por ser promocional
                        plan_acquired["is_active"] = True
                        plan_promotionals = SellerNonBillablePlans.objects.get(
                            query_plans=product["plan_id"],
                            seller=validated_data["seller"],
                            number_month=hoy.month)
                        plan_promotionals.quantity = plan_promotionals.quantity - 1
                        plan_promotionals.save()
                        sale_detail["discount"] = float(product["plan_id"].price)
                    sale_detail["product_type"] = product["product_type"]
                    sale_detail["sale"] = instance
                    # creamos la instancia de detalle
                    instance_sale = SaleDetail.objects.create(**sale_detail)
                    # llenamos data del plan adquirido
                    plan_acquired["validity_months"] = product["plan_id"].validity_months
                    plan_acquired["available_queries"] = product["plan_id"].query_quantity
                    plan_acquired["query_quantity"] = product["plan_id"].query_quantity
                    plan_acquired["available_requeries"] = 10  # harcoded. CAMBIAR
                    plan_acquired["maximum_response_time"] = 24  # harcoded.CAMBIAR
                    plan_acquired["plan_name"] = product["plan_id"].name
                    plan_acquired["query_plans"] = product["plan_id"]
                    plan_acquired["sale_detail"] = instance_sale
                    ins_plan = QueryPlansAcquired.objects.create(**plan_acquired)

                    QueryPlansClient.objects.create(
                        acquired_plan=ins_plan, status=1,
                        client=validated_data["client"])

        return instance

    def get_total_amount(self, products):
        """obtener el precio total."""
        acum = 0.00
        # recorro todos los productos
        for product in products:
            # debo asegurarme extraer el precio de los que son  planes
            if product["product_type"].id == 1:
                if product["is_billable"]:
                    acum += float(product["plan_id"].price)

        return acum
