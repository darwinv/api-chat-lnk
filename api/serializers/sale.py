"""Serializer de Venta"""
from rest_framework import serializers
from api.models import QueryPlansAcquired, QueryPlansClient, QueryPlansManage
from api.models import QueryPlans, Client
from api.models import SellerNonBillablePlans
from api.utils.tools import get_date_by_time
from datetime import datetime


class SaleSerializer(serializers.Serializer):
    """Serializer  de venta."""
    seller = 
