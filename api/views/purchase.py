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
from api.permissions import IsAdmin, IsSeller


class CreatePurchase(APIView):
    """Vista para crear compra."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdmin, IsSeller]

    def post(self, request):
        """metodo para crear compra."""

        user_id = Operations.get_id(self, request)
        data = request.data
        serializer = SaleSerializer(data=data)
        if serializer.is_valid():
            import pdb; pdb.set_trace()
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
