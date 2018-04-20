"""Activacion y modificacion de planes."""
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from api.serializers.plan import PlanDetailSerializer, ActivePlanSerializer
from api.serializers.plan import QueryPlansAcquiredSerializer
from api.models import QueryPlansAcquired
from api.permissions import IsAdminOrClient
from api.utils.validations import Operations
from api import pyrebase
from django.db.models import F
from django.http import Http404
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from datetime import datetime


class QueryPlansAcquiredDetailView(APIView):
    """Detalle de Plan Adquirido."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)

    def get_object(self, pk):
        """Obtener Objeto."""
        try:
            obj = QueryPlansAcquired.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """Obtener el Plan."""
        det_plan = self.get_object(pk)
        plan = QueryPlansAcquiredSerializer(det_plan)
        return Response(plan.data)

    def put(self, request, pk):
        """Activar el plan requrido y desactivar los demas."""
        client_id = Operations.get_id(self, request)
        data = request.data
        plan = self.get_object(pk)
        # valido el plan que se desea activar
        if (plan.is_active is True and plan.client_id == client_id and
                plan.expiration_date >= datetime.now().date()):
            serializer = QueryPlansAcquiredSerializer(plan, data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # sincronizo en pyrebase
                pyrebase.chosen_plan('u'+str(client_id), serializer.data)
            # traigo todos los demas planes
            plan_list = QueryPlansAcquired.objects.filter(
                client_id=client_id).exclude(pk=pk)
            # actualizo el campo is_chosen
            if plan_list.count() > 0:
                plan_list.update(is_chosen=False)
            return Response(serializer.data)
        raise Http404


class ClientPlansView(ListCreateAPIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)

    def get_object(self, pk):
        """Obtener lista de planes."""
        try:
            obj = QueryPlansAcquired.objects.filter(client=pk,
                                                    is_active=True,
                                                    expiration_date__gte=datetime.now().date())
            self.check_object_permissions(self.request, obj)
            return obj
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

    def get(self, request):
        """Obtener la lista con todos los planes del cliente."""
        id = request.user.id
        plan = self.get_object(id)
        serializer = QueryPlansAcquiredSerializer(plan, many=True)
        # paginacion
        page = self.paginate_queryset(plan)
        if page is not None:
            serializer = QueryPlansAcquiredSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)


class ActivationPlanView(APIView):
    """Activar pllan por codigo PIN.

    Si activa el plan y aun no tiene ninguno elegido para consultar
    este se elige automaticamente
    """

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        """Buscar plan adquirido."""
        try:
            return QueryPlansAcquired.objects.get(pk=pk)
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

    def get(self, request, code):
        """Devuelve la informacion del plan segun el codigo pasado."""
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

        # activation_date = datetime.now().date()
        if self.get_some_chosen_plan(client):
            is_chosen = False
        else:
            is_chosen = True

        plan_acquired = self.get_detail_plan(code, client)
        query_set = self.get_object(plan_acquired['id'])

        serializer = ActivePlanSerializer(query_set, data,
                                          context={'is_chosen': is_chosen},
                                          partial=True)
        # import pdb
        if serializer.is_valid():
            serializer.save()
            pyrebase.chosen_plan('u'+str(client), serializer.data)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_some_chosen_plan(self, client):
        """
            retorna True si el cliente ya tiene plan seleccionado
            retorna False si el cliente no tiene plan seleccionado
        """
        try:
            QueryPlansAcquired.objects.values('is_chosen')\
                .filter(client= client, is_active = True, is_chosen = True)[:1].get()
            return True
        except QueryPlansAcquired.DoesNotExist:
            return False

    def get_detail_plan(self, code, client):
        """Obtener detalle del plan por codigo de pin.

        Si no esta activo
        """
        try:
            # EL SIGUIENTE QUERY DEBE SER OPTIMIZADO Y REUTILIZADO PARA DIFERENTES SERVICIOS
            # Query para traer el detalle de un plan por el codigo PIN
            plan = get_query_set_plan()
            return plan.filter(client=client, sale_detail__pin_code=code,
                               is_active=False)[:1].get()

        except QueryPlansAcquired.DoesNotExist:
            raise Http404


    def get_some_chosen_plan(self, client):
        """
            retorna True si el cliente ya tiene plan seleccionado
            retorna False si el cliente no tiene plan seleccionado
        """
        try:
            QueryPlansAcquired.objects.values('is_chosen').filter(
                client=client, is_active=True, is_chosen=True)[:1].get()
            return True
        except QueryPlansAcquired.DoesNotExist:
            return False


class ChosenPlanView(APIView):
    """Devuelve plan principal del cliente que envia el token."""

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
            return plan_chosen.filter(client= client, is_active = True, is_chosen = True)[:1].get()

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
