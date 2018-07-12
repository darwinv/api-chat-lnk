"""Activacion y modificacion de planes."""
import sys
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from api.serializers.plan import PlanDetailSerializer, ActivePlanSerializer
from api.serializers.plan import QueryPlansAcquiredSerializer, QueryPlansAcquiredDetailSerializer
from api.serializers.plan import QueryPlansTransfer
from api.models import QueryPlansAcquired, QueryPlansClient, Client
from api.permissions import IsAdminOrClient
from api.utils.validations import Operations
from api.utils.querysets import get_query_set_plan
from api import pyrebase
from django.db.models import F
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from datetime import datetime
from rest_framework import serializers


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
        
        try:
            plan_client = QueryPlansClient.objects.get(client=client_id, acquired_plan=plan.id)
        except QueryPlansAcquired.DoesNotExist:
            raise Http404
        
        # valido el plan que se desea activar
        if (plan.is_active is True and plan_client.client_id == client_id and
                plan.expiration_date >= datetime.now().date()):
            serializer = QueryPlansAcquiredSerializer(plan, data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # sincronizo en pyrebase
                pyrebase.chosen_plan('u'+str(client_id), serializer.data)
            # traigo todos los demas planes
            plan_list = QueryPlansAcquired.objects.filter(
                queryplansclient__client=client_id).exclude(pk=pk)
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
            obj = QueryPlansAcquired.objects.filter(queryplansclient__client=pk,
                                                    is_active=True,
                                                    expiration_date__gte=datetime.now().date()).order_by('id')
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


class ClientPlansDetailView(ListCreateAPIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)

    def get(self, request, pk):
        """Obtener la lista con todos los planes del cliente."""
        client = Operations.get_id(self, request)
        plan = QueryPlansAcquired.objects.filter(pk=pk, queryplansclient__client=client).values('id', 'plan_name', 'is_chosen', 'is_active',
                  'validity_months', 'query_quantity',
                  'available_queries', 'expiration_date', 'queryplansclient__transfer',
                  'queryplansclient__share', 'queryplansclient__empower', 'queryplansclient__owner')
        
        if plan:
            serializer = QueryPlansAcquiredDetailSerializer(plan[0], partial=True)
            return Response(serializer.data)
        else:
            raise Http404

class ClientTransferPlansView(APIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)
    required = _("required")

    def post(self, request):
        """Obtener la lista con todos los planes del cliente."""
        client = Operations.get_id(self, request)
        data = request.data

        if not 'acquired_plan' in data:
            raise serializers.ValidationError({'acquired_plan': [self.required]})

        try:
            acquired_plan = QueryPlansAcquired.objects.get(pk=data['acquired_plan'],
             queryplansclient__client=client)
        except QueryPlansAcquired.DoesNotExist:
            raise Http404    

        email_receiver = receiver = None
        if 'email' in data:
            email_receiver = data['email']

        try:
            receiver = Client.objects.get(email_exact=email_receiver)
            status_transfer = 1
        except Client.DoesNotExist:
            status_transfer = 3
        

        if not email_receiver and not receiver:
            raise serializers.ValidationError({'email': [self.required]})

        data_transfer = {
            'type_operation': 3,  # transferencia
            'status': status_transfer,
            'acquired_plan': acquired_plan.id,
            'new_acquired_plan': None,
            'sender': client,
            'receiver': receiver,
            'email_receiver': email_receiver
        }
        data_context = {}
        data_context['client_receiver'] = {
            'owner': True,
            'transfer': True,
            'share': True,
            'empower': True,
            'status': status_transfer,
            'acquired_plan': acquired_plan,
            'client': receiver
        }
        data_context['client_sender'] = {
            'acquired_plan': acquired_plan.id,
            'client': client
        }
        serializer = QueryPlansTransfer(data=data_transfer, context=data_context)
        
        if serializer.is_valid():
            if 'test' not in sys.argv:
                if acquired_plan.is_chosen:  # Si el plan estaba escogido
                    pyrebase.delete_actual_plan_client(client)
                # send email
            serializer.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientAllPlansView(ListCreateAPIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)

    def get_object(self, pk):
        """Obtener lista de planes."""
        try:
            obj = QueryPlansAcquired.objects.filter(queryplansclient__client=pk).values('id',
                'plan_name', 'is_chosen', 'is_active',
                'validity_months', 'query_quantity',
                'available_queries', 'expiration_date', 'queryplansclient__transfer',
                'queryplansclient__share', 'queryplansclient__empower', 'queryplansclient__owner'
                ).order_by('id')
            self.check_object_permissions(self.request, obj)
            return obj
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

    def get(self, request):
        """Obtener la lista con todos los planes del cliente."""
        id = request.user.id
        plan = self.get_object(id)
        serializer = QueryPlansAcquiredDetailSerializer(plan, many=True)
        # paginacion
        page = self.paginate_queryset(plan)
        if page is not None:
            serializer = QueryPlansAcquiredDetailSerializer(page, many=True)
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
        has_chosen = False

        # activation_date = datetime.now().date()
        if self.get_some_chosen_plan(client):
            has_chosen = True
            is_chosen = False
        else:
            is_chosen = True

        plan_acquired = self.get_detail_plan(code, client)
        query_set = self.get_object(plan_acquired['id'])

        serializer = ActivePlanSerializer(query_set, data,
                                          context={'is_chosen': is_chosen},
                                          partial=True)
        # import pdb; pdb.set_trace()
        if serializer.is_valid():
            serializer.save()
            if not has_chosen:
                # print('no deberia  de entrar')
                if 'test' not in sys.argv:
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
                .filter(queryplansclient__client= client, is_active = True, is_chosen = True)[:1].get()
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
            return plan.filter(queryplansclient__client=client, sale_detail__pin_code=code,
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
                queryplansclient__client=client, is_active=True, is_chosen=True)[:1].get()
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
            return plan_chosen.filter(queryplansclient__client= client, is_active = True, is_chosen = True)[:1].get()

        except QueryPlansAcquired.DoesNotExist:
            raise Http404
