"""Activacion y modificacion de planes."""
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from api.serializers.plan import PlanDetailSerializer, ActivePlanSerializer, QueryPlansAcquiredSerializer 
from api.models import QueryPlansAcquired
from api.permissions import IsAdminOrOwner, IsAdminOrClient
from api.utils.tools import Operations
from django.db.models import F
from django.http import Http404

from datetime import datetime

class QueryPlansAcquiredDetailView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAdminOrClient,)

    def get_object(self, pk):

        try:
            obj = QueryPlansAcquired.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

    # detalle de plan
    def get(self, request, pk):
        det_plan = self.get_object(pk)
        plan = QueryPlansAcquiredSerializer(det_plan)
        return Response(plan.data)

    # actualizacion
    def put(self, request, pk):
        #Activar el plan requrido y desactivar los demas
        data = request.data
        client_id = Operations.get_id(self, request)

        plan = self.get_object(pk)

        #valido el plan que se desea activar
        if plan.is_active == True and plan.cliente_id == client_id and plan.expiration_date >= datetime.now().date():
            serializer = QueryPlansAcquiredSerializer(plan, data, partial=True)
            if serializer.is_valid():
                serializer.save()

            #traigo todos los demas planes
            plan_list = QueryPlansAcquired.objects.filter(cliente_id=client_id).exclude(pk=pk)
            # actualizo el campo is_chosen
            if plan_list.count() > 0:
                plan_list.update(is_chosen=False)
            return Response(serializer.data)
        raise Http404
        # raise serializers.ValidationError("plan_correct {}".format(required))


class ClientPlansView(ListCreateAPIView):
    #Vista para obetener todo los planes de un cliente
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAdminOrOwner,)

    def get_object(self, pk):
        """Obtener lista de planes."""
        try:
            obj = QueryPlansAcquired.objects.filter(cliente=pk, is_active = True, expiration_date__gte = datetime.now().date())
            # self.check_object_permissions(self.request, obj)
            return obj
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

    def get(self, request):
        #obtener la lista con todos los planes del cliente

        id = request.user.id
        client = self.get_object(id)
        serializer = QueryPlansAcquiredSerializer(client, many=True)
        #paginacion
        page = self.paginate_queryset(client)
        if page is not None:            
            serializer = QueryPlansAcquiredSerializer(page, many=True)
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