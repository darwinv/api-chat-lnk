"""Activacion y modificacion de planes."""
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import permissions
from api.models import Client
from django.http import Http404
from rest_framework.response import Response
from api.serializers.plan import PlanDetailSerializer, ActivePlanSerializer, QueryPlansAcquiredSerializer 
from api.models import QueryPlansAcquired
from django.db.models import F
from rest_framework import status
from api.permissions import IsAdminOnList, IsAdminOrOwner
from rest_framework.generics import ListCreateAPIView

class ClientPlansView(ListCreateAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAdminOrOwner,)

    def get_object(self, pk):
        """Obtener objeto."""
        try:
            obj = QueryPlansAcquired.objects.filter(cliente=2)
            #obj = QueryPlansAcquired.objects.all()
            self.check_object_permissions(self.request, obj)
            return obj
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

    def get(self, request):

        id = request.user.id
        client = self.get_object(id)
        serializer = QueryPlansAcquiredSerializer(client, many=True)

        page = self.paginate_queryset(client)
        if page is not None:            
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)

class ActivationPlanView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return QueryPlansAcquired.objects.get(pk=pk)
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

    def get(self, request, code):
        client = request.user.id
        query_set = self.get_detail_plan(code, client)
        try:
            serializer = PlanDetailSerializer(query_set)
            return Response(serializer.data)
        except Exception as e:
            print(e)
            raise Http404

    def put(self, request, code):
        """Activar producto, via codigo PIN."""
        data = request.data        
        client = request.user.id

        if self.get_some_chosen_plan(client):
            is_chosen = False
        else:
            is_chosen = True

        plan_acquired = self.get_detail_plan(code, client)
        query_set = self.get_object(plan_acquired['id'])

        serializer = ActivePlanSerializer(query_set, data, context={'is_chosen': is_chosen}, partial=True)
        # import pdb
        # pdb.set_trace()
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get_detail_plan(self, code, client):
        try:
            # EL SIGUIENTE QUERY DEBE SER OPTIMIZADO Y REUTILIZADO PARA DIFERENTES SERVICIOS
            # Query para traer el detalle de un plan por el codigo PIN
            plan = get_query_set_plan()

            return plan.filter(sale_detail__sale__client= client, sale_detail__pin_code=code, is_active = False)[:1].get()
            
        except QueryPlansAcquired.DoesNotExist:
            raise Http404


    def get_some_chosen_plan(self, client):
        """
            retorna True si el cliente ya tiene plan seleccionado
            retorna False si el cliente no tiene plan seleccionado
        """
        try:
            QueryPlansAcquired.objects.values('is_chosen')\
                .filter(sale_detail__sale__client= client, is_active = True, is_chosen = True)[:1].get()
            return True
        except QueryPlansAcquired.DoesNotExist:
            return False

class ChosemPlanView(APIView):
    """
        Vista para devolver plan principal del cliente que envia el token
    """
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        client = request.user.id

        data = self.get_detail_plan(client)
        
        try:
            serializer = PlanDetailSerializer(data)
            return Response(serializer.data)
        except Exception as e:
            print(e)
            raise Http404

    def get_detail_plan(self, client):
        """
        Funcion buscar el plan activo del cliente
        :param client: id del cliente
        :return: diccionario con informacion del plan
        """
        try:
            plan_chosen = get_query_set_plan()
            return plan_chosen.filter(sale_detail__sale__client= client, is_active = True, is_chosen = True)[:1].get()

        except QueryPlansAcquired.DoesNotExist:
            raise Http404

def get_query_set_plan():
    """
    Funcion creada para instancia base de los planes de un cliente
    :return: QuerySet
    """
    return QueryPlansAcquired.objects.values('id', 'is_chosen', 'is_active', 'plan_name',
                                              'query_quantity', 'available_queries',
                                              'validity_months','expiration_date','sale_detail__price')\
            .annotate(price=F('sale_detail__price'))