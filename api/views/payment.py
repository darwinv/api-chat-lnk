"""Vista de Pagos."""
import sys
from api.utils.tools import display_specialist_name, display_client_name
from api.serializers.payment import PaymentSerializer, PaymentSaleSerializer
from api.serializers.payment import PaymentSalePendingDetailSerializer
from api.serializers.payment import PaymentMatchSerializer
from api.serializers.payment import PaymentMatchClientSerializer
from api.serializers.payment import SaleContactoDetailSerializer
from api.serializers.sale import increment_reference
from api.utils.validations import Operations
from api.utils.querysets import get_next_fee_to_pay
from api.permissions import IsAdminOrSeller, IsAdmin, isAdminBackWrite
from api.permissions import IsAdminOrSpecialist
from api.serializers.notification import NotificationClientSerializer
from api.serializers.notification import NotificationSpecialistSerializer
from api.models import Sale, MonthlyFee, Client, Match, SaleDetail, Specialist
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, serializers
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListCreateAPIView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as trans
from django.db.models import Subquery, Q, OuterRef
from api.utils.parameters import Params
from api.logger import manager
from fcm.fcm import Notification

logger = manager.setup_log(__name__)


class CreatePayment(APIView):
    """Vista para crear pago."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, isAdminBackWrite,)

    def post(self, request):
        """crear compra."""
        data = request.data
        user_id = Operations.get_id(self, request)

        if "monthly_fee" in data:
            try:
                mfee = MonthlyFee.objects.get(pk=data["monthly_fee"])
                data["file_url"] = mfee.sale.file_url
                data["file_preview_url"] = mfee.sale.file_preview_url
            except Match.DoesNotExist:
                data["file_url"] = ""
                data["file_preview_url"] = ""
                logger.warning("no file_url para fee:" + mfee.id)

        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ConfirmDiscountView(APIView):
    """Confirmar descuento."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSpecialist]

    def put(self, request, pk):
        """Redefinido put"""
        try:
            match = Match.objects.get(pk=pk, status=2)
        except Match.DoesNotExist:
            raise Http404

        client = match.client
        # se verifica si ya fue cliente el usuario que solicito el match
        # si ya lo fue pasa a status 5 directo sino pasa a 4. pendiente de pago
        is_client = Sale.objects.filter(saledetail__is_billable=True,
                                        client=client,
                                        status__range=(2, 3)).exists()
        if is_client:
            match.status = 5
            disp_name_to_client = display_specialist_name(match)
            ticker_client = trans("successful hiring")
            disp_name_to_specialist = display_client_name(client)
            ticker_specialist = trans("successful hiring")
        else:
            match.status = 4
            disp_name_to_client = "Sube el recibo de tu pago"
            ticker_client = "Realiza tu pago, procederemos con tu solicitud"
            ticker_specialist = "Espera por el pago del cliente"
            disp_name_to_specialist = "Se autorizo tu solicitud de descuento"

        if 'test' not in sys.argv:
            client_id = match.client_id
            specialist_id = match.specialist_id
            qset_client = Client.objects.filter(pk=client_id)
            qset_spec = Specialist.objects.filter(pk=specialist_id)
            dict_pending_cl = NotificationClientSerializer(qset_client).data
            dict_pending_sp = NotificationSpecialistSerializer(qset_spec).data
            badge_count = dict_pending_cl["queries_pending"] + dict_pending_cl["match_pending"]
            badge_count_sp = dict_pending_sp["queries_pending"] + dict_pending_sp["match_pending"]

            data_client = {
                "title": disp_name_to_client,
                "body": match.subject,
                "sub_text": "",
                "ticker": ticker_client,
                "badge": badge_count,
                "icon": match.category.image,
                "type": Params.TYPE_NOTIF["match_success"],
                "queries_pending": dict_pending_cl["queries_pending"],
                "match_pending": dict_pending_cl["match_pending"],
                "match_id": match.id
            }
            data_specialist = {
                "title": disp_name_to_specialist,
                "body": match.subject,
                "sub_text": "",
                "ticker": ticker_specialist,
                "badge": badge_count_sp,
                "icon": match.category.image,
                "type": Params.TYPE_NOTIF["match_success"],
                "queries_pending": dict_pending_sp["queries_pending"],
                "match_pending": dict_pending_sp["match_pending"],
                "match_id": match.id
            }
            # envio de notificacion push
            Notification.fcm_send_data(user_id=client_id, data=data_client)
            Notification.fcm_send_data(user_id=specialist_id,
                                       data=data_specialist)
        match.save()

        return Response({"confirmado"}, status.HTTP_200_OK)

class MatchPaymentSpecialist(APIView):
    """Vista para crear pago de match specialista."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, isAdminBackWrite,)

    def post(self, request):
        """crear compra."""
        data = request.data

        if "match" in data:
            try:
                match = Match.objects.get(pk=data["match"])
            except Match.DoesNotExist:
                raise Http404

            data["file_url"] = match.file_url
            data["file_preview_url"] = match.file_preview_url

        serializer = PaymentMatchSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class MatchPaymentClient(APIView):
    """Vista para crear pago de match specialista."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, isAdminBackWrite,)

    def post(self, request):
        """crear compra."""
        data = request.data
        if "match" in data:
            sale = Match.objects.filter(pk=data["match"]
                                ).values("sale_detail__sale__file_url",
                                         "sale_detail__sale__file_preview_url").first()

            data["file_url"] = sale["sale_detail__sale__file_url"]
            data["file_preview_url"] = sale["sale_detail__sale__file_preview_url"]

        serializer = PaymentMatchClientSerializer(data=data)
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
                            status__in=[1,3]
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


class ClientHaveSalePending(ListCreateAPIView):
    """Vista para traer pagos pendientes."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)
    required = _("required")

    def get(self, request):
        """Detalle."""
        """Detalle de venta para contacto efectivo, devuelve ventas con
        paginacion para un cliente dado"""
        data = request.query_params
        if 'client' not in data:
            raise serializers.ValidationError({'client': [self.required]})

        client = data['client']

        have_pending_plans = Sale.objects.filter(saledetail__product_type=1,
                                        saledetail__is_billable=True,
                                        client=client,
                                        status=1,
                                        file_url="").values('id').first()

        if have_pending_plans:
            sale = Sale.objects.get(client=client, status=1, pk=have_pending_plans['id'])
        else:
            raise Http404

        serializer = SaleContactoDetailSerializer(sale)
        return Response(serializer.data)

class ClientSaleDetail(ListCreateAPIView):
    """Vista de detalle de venta."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)
    required = _("required")

    def get(self, request, sale_id):
        """Detalle."""
        """Detalle de venta para contacto efectivo, devuelve ventas con
        paginacion para un cliente dado"""
        data = request.query_params
        if not sale_id:
            raise serializers.ValidationError({'sale id': [self.required]})

        try:
            if request.user.role_id == 1: # admin
                sale = Sale.objects.get(pk=sale_id)
            elif request.user.role_id == 2: # client
                sale = Sale.objects.get(client=request.user.id, pk=sale_id)
            elif request.user.role_id == 4: # seller
                sale = Sale.objects.get(seller=request.user.id, pk=sale_id)
        except Sale.DoesNotExist:
            return Response({})

        serializer = SaleContactoDetailSerializer(sale)
        return Response(serializer.data)
