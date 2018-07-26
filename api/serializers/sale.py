"""Serializer de Venta"""
from rest_framework import serializers
from api.models import QueryPlansAcquired, QueryPlansClient, QueryPlansManage
from api.models import QueryPlans, Client, Seller, ProductType
from api.models import SellerNonBillablePlans
from api.utils.tools import get_date_by_time
from datetime import datetime


class ProductSerializer(serializers.Serializer):
    """Serializer para compra de producto."""

    product_type = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(), required=True)


class SaleSerializer(serializers.Serializer):
    """Serializer de venta."""
    # vendedor es  opcional, ya que puede comprar el cliente por su cuenta
    seller = serializers.PrimaryKeyRelatedField(queryset=Seller.objects.all())
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(),
                                                required=True)
    # listado de  productos que se agregaran en la venta
    products = serializers.ListField(child=ProductSerializer(), required=True)
