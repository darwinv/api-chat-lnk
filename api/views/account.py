"""Vista de Estado de Cuenta."""
from rest_framework.views import APIView
from api.serializers.account import SpecialistAccountSerializer
from api.serializers.account import SpecialistFooterSerializer
from api.serializers.account import SellerAccountSerializer
from api.serializers.account import SellerAccountBackendSerializer
from api.serializers.account import ClientAccountSerializer
from api.serializers.account import SellerFooterSerializer
from api.serializers.account import SellerAccountHistoricSerializer
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
import django_filters.rest_framework
from api.utils.validations import Operations
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.http import Http404
from api.models import Specialist, Query, Seller, Sale, Client
from api.models import QueryPlansClient
from rest_framework.pagination import PageNumberPagination
from api.permissions import IsSpecialist, IsSeller


# Vista para estado de cuenta de especialista
class SpecialistAccountView(APIView):
    """Vista para estado de cuenta de especialista."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Specialist.objects.get(pk=pk)
        except Specialist.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        specialist = self.get_object(pk)
        queryset = Query.objects.filter(specialist=specialist)
        # import pdb; pdb.set_trace()
        serializer = SpecialistAccountSerializer(queryset,
                                                 context={'category': specialist.category,
                                                          'specialist': specialist
                                                          })
        return Response(serializer.data)


class SpecialistFooterView(APIView):
    """Vista para footer del specialista."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsSpecialist]

    def get_object(self, pk):
        try:
            return Specialist.objects.get(pk=pk)
        except Specialist.DoesNotExist:
            raise Http404

    def get(self, request):
        pk = Operations.get_id(self, request)
        specialist = self.get_object(pk)
        queryset = Query.objects.filter(specialist=specialist)
        serializer = SpecialistFooterSerializer(queryset,
                                                context={'category': specialist.category,
                                                         'specialist': specialist
                                                         })
        return Response(serializer.data)


class ClientAccountView(APIView):
    """Vista para estadp de cuenta Cliente."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        client = self.get_object(pk)
        queryset = QueryPlansClient.objects.filter(client=client)
        serializer = ClientAccountSerializer(queryset,
                                             context={"client": client})
        return Response(serializer.data)


class SellerAccountView(APIView):
    """Vista para estado de cuenta de vendedor."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = (OAuth2Authentication,)
    queryset = Seller.objects.all()

    def get_object(self, pk):
        try:
            return Seller.objects.get(pk=pk)
        except Seller.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        seller = self.get_object(pk)
        queryset = Sale.objects.filter(seller=seller)
        serializer = SellerAccountSerializer(queryset,
                                             context={"seller": seller})
        return Response(serializer.data)


class SellerAccountBackendView(APIView):
    """Vista para estado de cuenta del backend vendedor."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Seller.objects.get(pk=pk)
        except Seller.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        seller = self.get_object(pk)
        queryset = Sale.objects.filter(seller=seller)

        serializer = SellerAccountSerializer(queryset,
                                             context={
                                                "seller": seller
                                            })

        serializer_historic = SellerAccountHistoricSerializer(queryset,
                                             context={
                                                "seller": seller
                                            })
        return Response({
                    'mounth':serializer.data,
                    'historic': serializer_historic.data
                    })


class SellerFooterView(APIView):
    """Vista del footer del vendedor."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_object(self, pk):
        try:
            return Seller.objects.get(pk=pk)
        except Seller.DoesNotExist:
            raise Http404

    def get(self, request):
        pk = Operations.get_id(self, request)
        seller = self.get_object(pk)
        queryset = Sale.objects.filter(seller=seller)
        serializer = SellerFooterSerializer(queryset,
                                            context={'seller': seller})
        return Response(serializer.data)
