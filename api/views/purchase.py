"""Vista de Compras y Ventas."""
from rest_framework.views import APIView
from api.serializers.sale import SaleSerializer
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
import django_filters.rest_framework
from api.utils.validations import Operations
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from api.permissions import IsAdminOrSeller
from api.models import Sale, SaleDetail, QueryPlansAcquired, QueryPlansClient
from api.models import MonthlyFee

class CreatePurchase(APIView):
    """Vista para crear compra."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """metodo para crear compra."""

        # user_id = Operations.get_id(self, request)
        extra = {}
        data = request.data
        user_id = Operations.get_id(self, request)
        # import pdb; pdb.set_trace()
        if request.user.role_id == 4:
            data["seller"] = user_id
        serializer = SaleSerializer(data=data, context=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

class PurchaseDetail(APIView):
    """Vista para crear compra."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        try:
            obj = Sale.objects.get(pk=pk, status=1)            
            if request.user.role_id != 1:
                # Es Dueño del plan
                if request.user.role_id == 2 and request.user.id == obj.client.id:
                    return obj
                # Es el vendedor asignado
                elif request.user.role_id == 4 and request.user.id == obj.client.seller_assigned.id:
                    return obj
                else:
                    raise Http404
            
            return obj
        except Sale.DoesNotExist:
            raise Http404

    def delete(self, request, pk):
        sale = self.get_object(request, pk)

        sale_detail = SaleDetail.objects.filter(sale=sale)

        query_plan = QueryPlansAcquired.objects.filter(sale_detail__in=sale_detail)
        query_plan_client = QueryPlansClient.objects.filter(acquired_plan__in=query_plan)
        monthly_fee = MonthlyFee.objects.filter(sale=sale)

        monthly_fee.delete()
        query_plan_client.delete()
        query_plan.delete()
        sale_detail.delete()
        sale.delete()
        return Response({})
