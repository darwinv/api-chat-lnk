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


class CreatePurchase(APIView):
    """Vista para crear compra."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSeller]

    def post(self, request):
        """metodo para crear compra."""

        # user_id = Operations.get_id(self, request)
        extra = {}
        data = request.data
        user_id = Operations.get_id(self, request)
        data["seller"] = user_id
        serializer = SaleSerializer(data=data, context=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
