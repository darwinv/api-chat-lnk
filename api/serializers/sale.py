"""Serializer de Venta"""
from rest_framework import serializers
from api.models import QueryPlansAcquired
from api.models import QueryPlans, Client, Seller, ProductType
from api.models import SellerNonBillablePlans, Sale
from api.utils.tools import get_date_by_time
from datetime import datetime


class ProductSerializer(serializers.Serializer):
    """Serializer para compra de producto."""

    product_type = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(), required=True)
    is_billable = serializers.BooleanField()
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=QueryPlans.objects.all(), required=False)
    discount = serializers.FloatField(min_value=0.00)


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


class SaleSerializer(serializers.Serializer):
    """Serializer de venta."""
    # vendedor es  opcional, ya que puede comprar el cliente por su cuenta
    seller = serializers.PrimaryKeyRelatedField(queryset=Seller.objects.all())
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(),
                                                required=True)
    # listado de  productos que se agregaran en la venta
    products = serializers.ListField(child=ProductSerializer(), required=True)
    is_fee = serializers.BooleanField(required=True)
    place = serializers.CharField()
    description = serializers.CharField(required=False)
    reference_number = serializers.CharField(default=increment_reference)

    def create(self, validated_data):
        """Metodo para guardar en venta."""
        total_amount = self.get_total_amount(validated_data["products"])
        print(validated_data["reference_number"])
        import pdb; pdb.set_trace()
        instance = Sale(**validated_data)
        # return Comment(**validated_data)

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
