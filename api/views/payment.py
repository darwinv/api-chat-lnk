"""Vista de Pagos."""
from api.serializers.payment import PaymentSerializer, PaymentSaleSerializer
from api.serializers.payment import PaymentSalePendingDetailSerializer
from api.serializers.payment import SaleContactoDetailSerializer
from api.utils.validations import Operations
from api.utils.querysets import get_next_fee_to_pay
from api.permissions import IsAdminOrSeller, IsAdmin, isAdminBackWrite
from api.models import Sale, MonthlyFee, Client
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, serializers
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListCreateAPIView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.db.models import Subquery, Q, OuterRef
import django_filters.rest_framework


class CreatePayment(APIView):
    """Vista para crear pago."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, isAdminBackWrite,)

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
        """get compra pendientes"""
        data = request.query_params

        fee = MonthlyFee.objects.filter(
                            sale=OuterRef("pk"),
                            status=1
                        )
        
        manage_data = Sale.objects.values('created_at',
            'total_amount','reference_number', 'is_fee', 'id',
            'client__first_name','client__last_name', 'client__business_name'
            ).filter(id__in=Subquery(fee.values('sale'))).annotate(
                                                            pay_before=Subquery(
                                                                fee.values(
                                                                    'pay_before')[:1]
                                                            )
                                                        ).order_by('pay_before')
        
        if 'document_number' in data:
            document = data['document_number']
            manage_data = manage_data.filter(Q(client__ruc=document) | Q(
                                        client__document_number= document))

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
        fee = get_next_fee_to_pay(pk)

        if fee:
            serializer = PaymentSalePendingDetailSerializer(fee)
            return Response(serializer.data)
        else:
            raise Http404


class PaymentDetailContactView(ListCreateAPIView):
    """Vista para traer pagos pendientes."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSeller)
    required = _("required")

    def get(self, request):
        """Detalle."""
        """Detalle de venta para contacto efectivo, devuelve ventas con
        paginacion para un cliente dado"""
        data = request.query_params
        if not 'email' in data:
            raise serializers.ValidationError({'email': [self.required]})

        email = data['email']
        try:
            client = Client.objects.get(email_exact=email)
        except Client.DoesNotExist:
            raise Http404

        sale = Sale.objects.filter(client=client)

        # paginacion
        page = self.paginate_queryset(sale)
        if page is not None:
            serializer = SaleContactoDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SaleContactoDetailSerializer(sale, many=True)
        return Response(serializer.data)
