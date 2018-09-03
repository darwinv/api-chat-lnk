"""Vista de Pagos."""
from rest_framework.views import APIView
from api.serializers.payment import PaymentSerializer, PaymentSaleSerializer
from api.serializers.payment import PaymentSaleDetailSerializer
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
import django_filters.rest_framework
from api.utils.validations import Operations
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from api.permissions import IsAdminOrSeller, IsAdmin
from api.models import Sale, MonthlyFee
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from django.db.models import Subquery, Q
from rest_framework.generics import ListCreateAPIView

class CreatePayment(APIView):
    """Vista para crear pago."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        """crear compra."""
        data = request.data
        user_id = Operations.get_id(self, request)
        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

class PaymentPendingView(ListCreateAPIView):
    """Vista para traer pagos pendientes."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAdmin,)
    required = _("required")

    def get(self, request):
        """get compra pendinetes"""
        data = request.query_params
        
        if not 'document_number' in data:
            raise serializers.ValidationError({'document_number': [self.required]})

        document = data['document_number']

        fee = MonthlyFee.objects.filter(status=1)

        manage_data = Sale.objects.values('created_at',
            'total_amount','reference_number', 'is_fee', 'id',
            'client__first_name','client__last_name', 'client__business_name'
            ).filter(
                Q(client__ruc=document) | Q(client__document_number= document),
                id__in=Subquery(fee.values('sale'))).order_by('-created_at')

        # paginacion
        page = self.paginate_queryset(manage_data)
        if page is not None:
            serializer = PaymentSaleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PaymentSaleSerializer(manage_data, many=True)
        return Response(serializer.data)

class PaymentPendingDetailView(APIView):
    """Vista para traer pagos pendientes."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAdmin,)

    def get(self, request, pk):
        """Detalle."""
        fee = MonthlyFee.objects.get(pk=pk)

        serializer = PaymentSaleDetailSerializer(fee)
        
        return Response(serializer.data)
