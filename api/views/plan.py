"""Activacion, modificacion y listado de planes."""
import sys
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from api.serializers.plan import PlanDetailSerializer, ActivePlanSerializer
from api.serializers.plan import QueryPlansAcquiredSerializer, QueryPlansAcquiredDetailSerializer
from api.serializers.plan import QueryPlansSerializer, QueryPlansManageSerializer
from api.serializers.plan import QueryPlansClientSerializer
from api.models import QueryPlans, Client, QueryPlansManage
from api.models import SellerNonBillablePlans
from api.serializers.plan import QueryPlansTransfer, QueryPlansShare, QueryPlansEmpower
from api.models import QueryPlansAcquired, QueryPlansClient
from api.permissions import IsAdminOrClient, IsSeller
from api.utils.validations import Operations
from api.utils.querysets import get_query_set_plan
from api.emails import BasicEmailAmazon
from api import pyrebase
from django.db.models import F,Q
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from datetime import datetime
from rest_framework import serializers
from linkupapi.settings_secret import WEB_HOST
from api.serializers.plan import PlansNonBillableSerializer


class PlansView(APIView):
    """Listado de planes activos a la venta."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request):
        """Devolver Planes."""
        q_plans = QueryPlans.objects.filter(is_active=True)
        plans = QueryPlansSerializer(q_plans, many=True)
        return Response(plans.data)


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
        """Elegir el plan requrido y desactivar los demas."""
        client_id = Operations.get_id(self, request)
        data = request.data
        plan = self.get_object(pk)

        try:
            plan_client = QueryPlansClient.objects.get(client=client_id, acquired_plan=plan.id)
        except QueryPlansClient.DoesNotExist:
            raise Http404

        # valido el plan que se desea activar
        if (plan.is_active is True and plan_client.client_id == client_id and
                plan.expiration_date >= datetime.now().date()):

            # Activar Plan
            serializer = QueryPlansClientSerializer(plan_client, data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # sincronizo en pyrebase
                data_pyresabe = {
                    'available_queries': plan.available_queries,
                    'expiration_date': str(plan.expiration_date),
                    'id': plan.id,
                    'is_active': plan.is_active,
                    'is_chosen': plan_client.is_chosen,
                    'plan_name': plan.plan_name,
                    'query_quantity': plan.query_quantity,
                    'validity_months': plan.validity_months,
                }
                pyrebase.chosen_plan(client_id, data_pyresabe)
                # traigo todos los demas planes
                plan_list = QueryPlansClient.objects.filter(
                    client=client_id).exclude(pk=pk)
                # actualizo el campo is_chosen
                if plan_list.count() > 0:
                    plan_list.update(is_chosen=False)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, HTTP_400_BAD_REQUEST)
        raise Http404


class ClientPlansView(ListCreateAPIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)

    def get_object(self, pk):
        """Obtener lista de planes."""
        plan = QueryPlansAcquired.objects.filter(is_active=True, queryplansclient__client=pk,
            expiration_date__gte=datetime.now().date()).order_by('id').values(
                  'id', 'plan_name', 'is_active',
                  'validity_months', 'query_quantity',
                  'available_queries', 'expiration_date').annotate(
                  is_chosen=F('queryplansclient__is_chosen')).order_by('id')
        if plan:
            return plan
        else:
            raise Http404

    # def get_object(self, pk):
    #     """Obtener lista de planes."""
    #     try:
    #         obj = QueryPlansAcquired.objects.filter(queryplansclient__client=pk,
    #                                                 is_active=True,
    #                                                 expiration_date__gte=datetime.now().date()).order_by('id')
    #         self.check_object_permissions(self.request, obj)
    #         return obj
    #     except QueryPlansAcquired.DoesNotExist:
    #         raise Http404

    def get(self, request):
        """Obtener la lista con todos los planes del cliente."""
        pk = Operations.get_id(self, request)
        plan = self.get_object(pk)

        # paginacion
        page = self.paginate_queryset(plan)
        if page is not None:
            serializer = QueryPlansAcquiredSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = QueryPlansAcquiredSerializer(plan, many=True)
        return Response(serializer.data)


class ClientPlansDetailView(ListCreateAPIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)

    def get(self, request, pk):
        """Obtener la lista con todos los planes del cliente."""
        client = Operations.get_id(self, request)
        plan = QueryPlansAcquired.objects.filter(pk=pk, queryplansclient__client=client).values(
                  'id', 'plan_name', 'is_active',
                  'validity_months', 'query_quantity',
                  'available_queries', 'expiration_date', 'queryplansclient__transfer',
                  'queryplansclient__share', 'queryplansclient__empower', 'queryplansclient__owner').annotate(
                  is_chosen=F('queryplansclient__is_chosen'))

        if plan:
            serializer = QueryPlansAcquiredDetailSerializer(plan[0], partial=True)
            return Response(serializer.data)
        else:
            raise Http404



class ClientSharePlansView(APIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)
    required = _("required")
    subject = _("Share Plan Success")
    to_much_query_share = _("too many queries to share")
    already_exists_empower = _("Empower already exists")

    def post(self, request):
        """Obtener la lista con todos los planes del cliente."""
        client = Operations.get_id(self, request)
        data = request.data

        if not 'acquired_plan' in data:
            raise serializers.ValidationError({'acquired_plan': [self.required]})

        if 'client' in data and type(data['client']) is list:
            clients = data['client']
        else:
            raise serializers.ValidationError({'client': [self.required]})

        try:
            acquired_plan = QueryPlansAcquired.objects.get(pk=data['acquired_plan'],
             queryplansclient__client=client, queryplansclient__share=True)
            acquired_plan_client = QueryPlansClient.objects.get(acquired_plan=acquired_plan,
             client=client)
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

        try:
            client_obj = Client.objects.get(pk=client)
        except Client.DoesNotExist:
            raise Http404

        errors = {}
        serializer_data = {}

        # Validar cantidad total de consultas
        acumulator = 0
        for client_data in clients:
            if 'count' in client_data:
                acumulator += int(client_data['count'])

        if acumulator > acquired_plan.available_queries:
            raise serializers.ValidationError({'count': [self.to_much_query_share]})

        for client_data in clients:
            email_receiver = receiver = count = None

            # Validamos si enviar el correo del cliente
            if 'email_receiver' in client_data:
                email_receiver = client_data['email_receiver']
            else:
                errors[email_receiver] = {'email_receiver': [self.required]}
                continue

            # Se valida que enviaron la cantidad
            if 'count' in client_data:
                count = int(client_data['count'])
            else:
                errors[email_receiver] = {'count': [self.required]}
                continue

            # Traer cliente by email si existe!
            try:
                receiver = Client.objects.get(email_exact=email_receiver)
                status_transfer = 1
            except Client.DoesNotExist:
                status_transfer = 3

            # No realizar operacion a sigo mismo
            if email_receiver == client_obj.email_exact:
                errors[email_receiver] = {'email_receiver': [self.invalid]}
                continue

            # No realizar operacion si tiene operacioens previas para este plan
            plan_manage = QueryPlansManage.objects.filter(
                Q(receiver=receiver, status=1) | Q(email_receiver=email_receiver, status=3)).filter(
                acquired_plan=acquired_plan.id, sender=client, type_operation=3)

            if plan_manage:
                errors[email_receiver] = {'email_receiver': [self.already_exists_empower]}
                continue

            data_manage = {
                'type_operation': 2,  # Compartir
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
                'acquired_plan': None,
                'client': receiver
            }
            data_context['count'] = count
            data_context['acquired_plan'] = acquired_plan
            serializer = QueryPlansShare(data=data_manage, context=data_context)

            if serializer.is_valid():
                serializer_data[email_receiver] = serializer
            else:
                errors[email_receiver] = serializer.errors

        # Se retornan los errores que se acumularon
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Para cada uno de los correos guardados
            for email_receiver in serializer_data:
                if 'test' not in sys.argv:
                        # Envio de correos notificacion
                        mail = BasicEmailAmazon(subject="Share Plan Success", to=email_receiver,
                                    template='email/share')
                        arguments = {'link': WEB_HOST}
                        mail.sendmail(args=arguments)

                # Ejecutamos el serializer
                serializer_data[email_receiver].save()

            if 'test' not in sys.argv:
                if acquired_plan_client.is_chosen:
                    data_plan = {
                        'available_queries': acquired_plan.available_queries
                    }
                    pyrebase.chosen_plan(client, data_plan)

            return Response({})


class ClientEmpowerPlansView(APIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)
    required = _("required")
    invalid = _("invalid")
    subject = _("Empower Plan Success")
    already_exists_empower = _("Empower already exists")
    already_exists_share = _("Share already exists")

    def post(self, request):
        """Obtener la lista con todos los planes del cliente."""
        client = Operations.get_id(self, request)
        data = request.data

        if not 'acquired_plan' in data:
            raise serializers.ValidationError({'acquired_plan': [self.required]})

        if 'client' in data and type(data['client']) is list:
            clients = data['client']
        else:
            raise serializers.ValidationError({'client': [self.required]})

        try:
            acquired_plan = QueryPlansAcquired.objects.get(pk=data['acquired_plan'],
             queryplansclient__client=client, queryplansclient__empower=True)
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

        try:
            client_obj = Client.objects.get(pk=client)
        except Client.DoesNotExist:
            raise Http404

        errors = {}
        serializer_data = {}
        for client_data in clients:
            email_receiver = receiver = None

            # Validamos si enviar el correo del cliente
            if 'email_receiver' in client_data:
                email_receiver = client_data['email_receiver']
            else:
                continue

            # Traer cliente by email si existe!
            try:
                receiver = Client.objects.get(email_exact=email_receiver)
                status_transfer = 1
            except Client.DoesNotExist:
                status_transfer = 3

            # No realizar operacion a sigo mismo
            if email_receiver == client_obj.email_exact:
                errors[email_receiver] = {'email_receiver': [self.invalid]}
                continue

            # No realizar operacion si tiene operacioens previas para este plan
            plan_manage = QueryPlansManage.objects.filter(
                Q(receiver=receiver, status=1) | Q(email_receiver=email_receiver, status=3)).filter(
                acquired_plan=acquired_plan.id, sender=client)

            if plan_manage:
                if plan_manage[0].type_operation == 3:
                    errors[email_receiver] = {'email_receiver': [self.already_exists_empower]}
                elif plan_manage[0].type_operation == 2:
                    errors[email_receiver] = {'email_receiver': [self.already_exists_share]}
                continue

            # Data del plan a Manejar
            data_manage = {
                'type_operation': 3,  # Facultar
                'status': status_transfer,
                'acquired_plan': acquired_plan.id,
                'new_acquired_plan': None,
                'sender': client,
                'receiver': receiver,
                'email_receiver': email_receiver
            }
            # Data de conexto para el cliente que recive plan
            data_context = {}
            data_context['client_receiver'] = {
                'owner': False,
                'transfer': True,
                'share': True,
                'empower': False,
                'status': status_transfer,
                'acquired_plan': acquired_plan,
                'client': receiver
            }

            serializer = QueryPlansEmpower(data=data_manage, context=data_context)

            if serializer.is_valid():
                serializer_data[email_receiver] = serializer
            else:
                errors[email_receiver] = serializer.errors

        # Se retornan los errores que se acumularon
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Para cada uno de los correos guardados
            for email_receiver in serializer_data:
                if 'test' not in sys.argv:
                        # Envio de correos notificacion
                        mail = BasicEmailAmazon(subject="Facultar Plan Exitoso", to=email_receiver,
                                    template='email/empower')
                        arguments = {'link': WEB_HOST}
                        mail.sendmail(args=arguments)

                # Ejecutamos el serializer
                serializer_data[email_receiver].save()

            return Response({})


class ClientTransferPlansView(APIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)
    required = _("required")
    subject = _("Transfer Plan Success")
    invalid = _("invalid")
    already_exists = _("it already exists")

    def post(self, request):
        """Obtener la lista con todos los planes del cliente."""
        client = Operations.get_id(self, request)
        data = request.data

        if not 'acquired_plan' in data:
            raise serializers.ValidationError({'acquired_plan': [self.required]})

        try:
            client_obj = Client.objects.get(pk=client)
        except Client.DoesNotExist:
            raise Http404

        try:
            acquired_plan = QueryPlansAcquired.objects.get(pk=data['acquired_plan'],
             queryplansclient__client=client, queryplansclient__transfer=True)
            acquired_plan_client = QueryPlansClient.objects.get(acquired_plan=acquired_plan,
             client=client)
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

        email_receiver = receiver = None
        if 'email_receiver' in data:
            email_receiver = data['email_receiver']

        try:
            receiver = Client.objects.get(email_exact=email_receiver)
            status_transfer = 1
        except Client.DoesNotExist:
            status_transfer = 3


        if not email_receiver and not receiver:
            raise serializers.ValidationError({'email_receiver': [self.required]})

        # No realizar operacion a sigo mismo
        if email_receiver == client_obj.email_exact:
            raise serializers.ValidationError({'email_receiver': [self.invalid]})

        # No realizar operacion si tiene operacioens previas para este plan
        plan_manage = QueryPlansManage.objects.filter(
            Q(receiver=receiver, status=1) | Q(email_receiver=email_receiver, status=3)).filter(
            acquired_plan=acquired_plan.id, sender=client)

        if plan_manage:
            raise serializers.ValidationError({'email_receiver': [self.already_exists]})

        data_transfer = {
            'type_operation': 1,  # transferencia
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
            'client': receiver,
            'is_chosen': False
        }
        data_context['client_sender'] = {
            'acquired_plan': acquired_plan.id,
            'client': client
        }
        is_chosen_plan = acquired_plan_client.is_chosen
        serializer = QueryPlansTransfer(data=data_transfer, context=data_context)

        if serializer.is_valid():
            if 'test' not in sys.argv:
                # Envio de correos notificacion
                mail = BasicEmailAmazon(subject="Facultar Plan Exitoso", to=email_receiver,
                            template='email/empower')
                arguments = {'link': WEB_HOST}
                mail.sendmail(args=arguments)

                # Si el plan estaba escogido por el anterior cliente
                if is_chosen_plan:
                    pyrebase.delete_actual_plan_client(client)

                    mail = BasicEmailAmazon(subject=self.subject, to=email_receiver,
                                template='email/transfer')

                    args = {
                        'link': WEB_HOST
                    }
                    mail.sendmail(args=request.data)

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
                'plan_name', 'queryplansclient__is_chosen', 'is_active',
                'validity_months', 'query_quantity',
                'available_queries', 'expiration_date', 'queryplansclient__transfer',
                'queryplansclient__share', 'queryplansclient__empower', 'queryplansclient__owner'
                ).annotate(is_chosen=F('queryplansclient__is_chosen')).order_by('id')
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
                                          context={
                                            'is_chosen': is_chosen,
                                            'client': client
                                            },
                                          partial=True)

        if serializer.is_valid():
            serializer.save()
            if not has_chosen:
                # print('no deberia  de entrar')
                if 'test' not in sys.argv:
                    pyrebase.chosen_plan(client, serializer.data)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_some_chosen_plan(self, client):
        """
            retorna True si el cliente ya tiene plan seleccionado
            retorna False si el cliente no tiene plan seleccionado
        """
        try:
            QueryPlansAcquired.objects.values('queryplansclient__is_chosen')\
                .filter(queryplansclient__client=client, is_active = True, queryplansclient__is_chosen = True)[:1].get()
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
            return plan_chosen.filter(queryplansclient__client= client, is_active = True, queryplansclient__is_chosen = True)[:1].get()

        except QueryPlansAcquired.DoesNotExist:
            raise Http404

class ClientCheckEmailOperationView(APIView):
    """Vista para checkar si un correo puede realizar operacion"""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)

    already_exists_empower = _("Empower already exists")
    required = _("required")
    invalid = _("invalid")
    already_exists_empower_or_share = _("Empower or Share already exists")
    def get(self, request):
        client = Operations.get_id(self, request)
        data = request.query_params
        response = True

        if 'acquired_plan' in data:
            acquired_plan = data['acquired_plan']
        else:
            raise serializers.ValidationError({'acquired_plan': [self.required]})

        if 'email_receiver' in data:
            email_receiver = data['email_receiver']
        else:
            raise serializers.ValidationError({'email_receiver': [self.required]})

        if 'type_operation' in data:
            type_operation = int(data['type_operation'])
        else:
            raise serializers.ValidationError({'type_operation': [self.required]})

        # No realizar operacion a sigo mismo
        try:
            client_obj = Client.objects.get(pk=client)
        except Client.DoesNotExist:
            raise Http404

        if email_receiver == client_obj.email_exact:
            raise serializers.ValidationError({'email_receiver': [self.invalid]})

        # Traer cliente by email si existe!
        try:
            receiver = Client.objects.get(email_exact=email_receiver)
            status_transfer = 1
        except Client.DoesNotExist:
            receiver = None
            status_transfer = 3

        if type_operation == 1 or type_operation == 3:
            """Transferir"""
            # No realizar operacion si tiene operacioens previas para este plan
            plan_manage = QueryPlansManage.objects.filter(
                Q(receiver=receiver, status=1) | Q(email_receiver=email_receiver, status=3)).filter(
                acquired_plan=acquired_plan, sender=client)

            if plan_manage:
                raise serializers.ValidationError({'email_receiver': [self.already_exists_empower_or_share]})

        if type_operation==2:
            """compartir"""
            # No realizar operacion si tiene operacioens previas para este plan
            plan_manage = QueryPlansManage.objects.filter(
                Q(receiver=receiver, status=1) | Q(email_receiver=email_receiver, status=3)).filter(
                acquired_plan=acquired_plan, sender=client, type_operation=3)

            if plan_manage:
                raise serializers.ValidationError({'email_receiver': [self.already_exists_empower]})

        # Cliente no existe pero puede ser facultado, compartido, transferido
        if not receiver:
            raise Http404

        return Response(response)


class ClientShareEmpowerPlansView(ListCreateAPIView):
    """Vista para clientes Compartidos y facultados"""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)

    def get(self, request, pk):
        client = Operations.get_id(self, request)
        data = request.data

        manage_data = QueryPlansManage.objects.values('email_receiver',
            'status','type_operation', 'receiver', 'new_acquired_plan'
            ).annotate(available_queries=F('new_acquired_plan__available_queries',),
            query_quantity=F('new_acquired_plan__query_quantity',),
            first_name=F('receiver__first_name',),
            last_name=F('receiver__last_name',),
            business_name=F('receiver__business_name',),
            type_client=F('receiver__type_client',),
            photo=F('receiver__photo',)).filter(acquired_plan = pk)

        # paginacion
        page = self.paginate_queryset(manage_data)
        if page is not None:
            serializer = QueryPlansManageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = QueryPlansManageSerializer(manage_data, many=True)
        return Response(serializer.data)


class PlansNonBillableView(APIView):
    """Vista para crear planes no facturables."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

    def post(self, request):
        """Ingresar en plan no facturable."""
        data = request.data
        serializer = PlansNonBillableSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class PlansNonBillableSellerView(APIView):
    """Vista para crear planes no facturables."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsSeller)

    def get(self, request):
        """Devolver Planes."""
        user_id = Operations.get_id(self, request)
        hoy = datetime.now()  # fecha de hoy
        q_plans = SellerNonBillablePlans.objects.filter(seller_id=user_id,
                                                        number_month=hoy.month)
        plans = PlansNonBillableSerializer(q_plans, many=True)
        return Response(plans.data)
