"""Vista de Compras y Ventas."""
from rest_framework.views import APIView
from api.serializers.sale import SaleSerializer
from api.serializers.actors import ContactToClientSerializer
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
import django_filters.rest_framework
from api.utils.validations import Operations
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from api.permissions import IsAdminOrSeller
from api.models import Sale, SaleDetail, QueryPlansAcquired, QueryPlansClient
from api.models import MonthlyFee, Client, SellerContact, ContactVisit
from api import pyrebase
from api.utils.querysets import is_assigned
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

class CreatePurchase(APIView):
    """Vista para crear compra."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated]
    required = _("required")

    def post(self, request):
        """metodo para crear compra."""
        # user_id = Operations.get_id(self, request)
        extra = {}
        data = request.data
        client = Client.objects.get(pk=data['client'])

        if request.user.role_id == 4:
            # Si es vendedor, se usa su id como el que efectuo la venta
            if 'latitude' in data:
                latitude = data["latitude"]
            else:
                raise serializers.ValidationError({'latitude': [self.required]})
            if 'longitude' in data:
                longitude = data["longitude"]
            else:
                raise serializers.ValidationError({'longitude': [self.required]})

            user_id = Operations.get_id(self, request)
            data['seller'] = user_id
        elif request.user.role_id == 1 or request.user.role_id == 2:
            # si se trata de un administrador o cliente, la venta la habra efectuado el vendedor asignado
            data['seller'] = client.seller_assigned.id

        serializer = SaleSerializer(data=data, context=data)
        if serializer.is_valid():
            serializer.save()

            contact = SellerContact.objects.get(client=client)
            if is_assigned(client=client, contact=contact):
                contact.is_assigned = False
                contact.save()

            if request.user.role_id == 4:
                # Guardar la visita del Vendedor
                if not data["products"][0]["is_billable"] and len(data["products"])==1:
                    # Si solo compra un promocional
                    type_visit = 4
                else:
                    type_visit = 1


                # Si es una compra anterior sin compra se actualiza la visita
                pending_visits = ContactVisit.objects.filter(contact=contact, type_visit=1,
                                                sale=None).order_by('-created_at')

                if pending_visits:
                    pending_visit = pending_visits[0]  # Tomar ultima visita con compra sin sale

                    pending_visit.sale = Sale.objects.get(pk=serializer.data["id"])
                    pending_visit.latitude = data['latitude']
                    pending_visit.longitude = data['longitude']
                    pending_visit.save()

                else:
                    visit_instance = ContactVisit.objects.create(contact=contact,
                                        type_visit=type_visit,
                                        latitude=data['latitude'],
                                        longitude=data['longitude'],
                                        sale=Sale.objects.get(pk=serializer.data["id"]))

                if type_visit == 4 and contact.type_contact == 2:
                    contact.type_contact = 4
                    contact.save()

            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ContactNoEffectivePurchase(APIView):
    """Vista para crear compra."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """metodo para crear compra."""
        # user_id = Operations.get_id(self, request)
        data = request.data
        user_id = Operations.get_id(self, request)
        if request.user.role_id == 4:
            # Si es vendedor, se usa su id como el que efectuo la venta
            data['seller'] = user_id
        elif request.user.role_id == 1 or request.user.role_id == 2:
            # si se trata de un administrador o cliente, la venta la habra efectuado el vendedor asignado
            data['seller'] = Client.objects.get(pk=data['client']).seller_assigned.id
        serializer_client = ContactToClientSerializer(data=data)
        if serializer_client.is_valid():
            serializer_client.save()
            data['client'] = serializer_client.data['client_id']

            # Categorias para usuario pyrebase
            pyrebase.createCategoriesLisClients(data['client'])
        else:
            return Response(serializer_client.errors, status.HTTP_400_BAD_REQUEST)

        serializer = SaleSerializer(data=data, context=data)
        if serializer.is_valid():
            serializer.save()

            contact = SellerContact.objects.get(client_id=data['client'])
            if is_assigned(contact=contact):
                if 'latitude' in data:
                    contact.latitude = data['latitude']
                if 'longitude' in data:
                    contact.longitude = data['longitude']

                contact.is_assigned = False
                contact.save()

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
