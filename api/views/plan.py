"""Activacion, modificacion y listado de planes."""
import json
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from api.serializers.plan import PlanDetailSerializer, ActivePlanSerializer
from api.serializers.plan import QueryPlansAcquiredSerializer, QueryPlansAcquiredDetailSerializer
from api.serializers.plan import QueryPlansSerializer, QueryPlansManageSerializer
from api.serializers.plan import QueryPlansClientSerializer
from api.serializers.plan import QueryPlansTransferSerializer, QueryPlansShareSerializer, QueryPlansEmpowerSerializer
from api.serializers.notification import NotificationClientSerializer
from api.models import QueryPlans, Client, QueryPlansManage
from api.models import SellerNonBillablePlans, SellerContact
from api.models import QueryPlansAcquired, QueryPlansClient
from api.permissions import IsAdminOrClient, IsSeller
from api.utils.validations import Operations
from api.utils.querysets import get_query_set_plan
from api.utils.tools import display_client_name
from api.utils.parameters import Params
from api.emails import BasicEmailAmazon
from api import pyrebase
import sys
from django.db.models import F,Q
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from datetime import datetime
from rest_framework import serializers
from linkupapi.settings_secret import WEB_HOST
from api.serializers.plan import PlansNonBillableSerializer, PlanStatusSerializer
from fcm.fcm import Notification

REGISTER_LINK = WEB_HOST + 'register'
REGISTRATION_MESSAGE = _('Please, click the following register link, fill your details and you will get your query plans')

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
            # import pdb; pdb.set_trace()
        except QueryPlansClient.DoesNotExist:
            raise Http404

        # valido el plan que se desea activar
        if (plan.is_active is True and plan_client.client_id == client_id and
                plan.expiration_date >= datetime.now().date()):

            # Activar Plan
            serializer = QueryPlansClientSerializer(plan_client, data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if 'test' not in sys.argv:
                    # sincronizo en pyrebase
                    plan_chosen = get_query_set_plan()
                    plan_active = plan_chosen.filter(queryplansclient__client=client_id, is_active=True,
                                                             queryplansclient__is_chosen=True)
                    serializer_plan_acquired = QueryPlansAcquiredSerializer(plan_active[0])
                    pyrebase.chosen_plan(client_id, serializer_plan_acquired.data)
                    result_data = serializer_plan_acquired.data
                else:
                    result_data = {}
                return Response(result_data)
            else:
                return Response(serializer.errors, HTTP_400_BAD_REQUEST)
        raise Http404


class ClientPlansView(ListCreateAPIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)

    def get_object(self, pk):
        """Obtener lista de planes."""
        plan = QueryPlansAcquired.objects.filter(
            is_active=True, queryplansclient__client=pk,
            available_queries__gt=0,
            expiration_date__gte=datetime.now().date()).order_by('id').values(
                  'id', 'plan_name', 'is_active',
                  'validity_months', 'query_quantity',
                  'available_queries', 'expiration_date', 'queries_to_pay').annotate(
                  is_chosen=F('queryplansclient__is_chosen')).order_by('id')
        if plan is not None:
            return plan
        else:
            raise Http404

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
        plan = QueryPlansAcquired.objects.filter(pk=pk, queryplansclient__client=client).values('id',
                 'plan_name', 'queryplansclient__is_chosen', 'is_active', 'status',
                 'validity_months', 'query_quantity', 'queries_to_pay', 'activation_date',
                 'available_queries', 'expiration_date', 'queryplansclient__transfer',
                 'queryplansclient__share', 'queryplansclient__empower', 'queryplansclient__owner').annotate(
                  is_chosen=F('queryplansclient__is_chosen'),
                  price=F('sale_detail__price'),
                  sale=F('sale_detail__sale'),
                  is_fee=F('sale_detail__sale__is_fee'))

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
    invalid = _("invalid")
    default_message = _("Please click the next link to get your plan share")
    subject = _("Share Plan Success")
    to_much_query_share = _("too many queries to share")
    already_exists_empower = _("Empower already exists")

    def post(self, request):
        """Obtener la lista con todos los planes del cliente."""
        client = Operations.get_id(self, request)
        data = request.data

        if not 'acquired_plan' in data:
            raise serializers.ValidationError({'acquired_plan': [self.required]})

        if 'client' in data:
            clients = data['client']
            if type(clients) is str:
                clients = json.loads(clients)

            if type(clients) is not list:
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
                qset_client = Client.objects.filter(pk=receiver.id)
            except Client.DoesNotExist:
                status_transfer = 3
                receiver = None

            # No realizar operacion si tiene operacioens previas para este plan
            plan_manage = QueryPlansManage.objects.filter(
                Q(receiver=receiver, status=1) | Q(email_receiver=email_receiver, status=3)).filter(
                acquired_plan=acquired_plan.id, sender=client)
            if plan_manage and plan_manage[0].type_operation == 3:
                errors[email_receiver] = {'email_receiver': [self.already_exists_empower]}
                continue
            elif not plan_manage:
                plan_manage = None
            else:
                plan_manage = plan_manage[0]

            checker = CheckEmailOperationPlan(2, email_receiver, acquired_plan, client_obj, receiver)
            if not checker.is_valid():
                errors[email_receiver] = checker.errors
                continue

            data_manage = {
                'type_operation': 2,  # Compartir
                'status': status_transfer,
                'acquired_plan': acquired_plan.id,
                'new_acquired_plan': None,
                'sender': client,
                'receiver': receiver,
                'email_receiver': email_receiver,
                'count_queries': count
            }
            data_context = {}
            data_context['client_receiver'] = {
                'is_chosen': False,
                'owner': False,
                'transfer': False,
                'share': False,
                'empower': False,
                'status': status_transfer,
                'acquired_plan': None,
                'client': receiver
            }
            data_context['count'] = count
            data_context['acquired_plan'] = acquired_plan
            data_context['plan_manage'] = plan_manage

            serializer = QueryPlansShareSerializer(data=data_manage, context=data_context)

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
                    mail = BasicEmailAmazon(subject=str(self.subject), to=email_receiver,
                                template='email/share')
                    if receiver is not None:
                        arguments = {'message':self.default_message, 'link':WEB_HOST}
                    else:
                        arguments = {'message':REGISTRATION_MESSAGE, 'link':REGISTER_LINK}
                    mail.sendmail(args=arguments)

                # Ejecutamos el serializer
                serializer_data[email_receiver].save()

                if 'test' not in sys.argv:
                    if status_transfer == 1:
                        new_acquired = serializer_data[email_receiver].data["new_acquired_plan"]
                        reciever_id = serializer_data[email_receiver].data["receiver"]
                        dict_pending = NotificationClientSerializer(qset_client).data
                        badge_count = dict_pending["queries_pending"] + dict_pending["match_pending"]
                        data_notif_push = {
                            "title": "Se te han compartido consultas",
                            "body": display_client_name(client_obj),
                            "sub_text": "",
                            "ticker": "",
                            "badge": badge_count,
                            "icon": client_obj.photo,
                            "plan_id": new_acquired,
                            "type": Params.TYPE_NOTIF["plan"],
                            "queries_pending": dict_pending["queries_pending"],
                            "match_pending": dict_pending["match_pending"]
                        }
                        # envio de notificacion push
                        Notification.fcm_send_data(user_id=reciever_id,
                                                   data=data_notif_push)
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
    default_message = _("Please click the next link to get your plan empower")
    subject = _("Empower Plan Success")
    already_exists_empower = _("Empower already exists")
    already_exists_share = _("Share already exists")

    def post(self, request):
        """Obtener la lista con todos los planes del cliente."""
        client = Operations.get_id(self, request)
        data = request.data

        if not 'acquired_plan' in data:
            raise serializers.ValidationError({'acquired_plan': [self.required]})

        if 'client' in data:
            clients = data['client']
            if type(clients) is str:
                clients = json.loads(clients)

            if type(clients) is not list:
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
                qset_client = Client.objects.filter(pk=receiver.id)
            except Client.DoesNotExist:
                status_transfer = 3
                receiver = None

            checker = CheckEmailOperationPlan(3, email_receiver, acquired_plan, client_obj, receiver)
            if not checker.is_valid():
                errors[email_receiver] = checker.errors
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
                'is_chosen': False,
                'owner': False,
                'transfer': False,
                'share': True,
                'empower': False,
                'status': status_transfer,
                'acquired_plan': acquired_plan,
                'client': receiver
            }

            serializer = QueryPlansEmpowerSerializer(data=data_manage, context=data_context)

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
                # Ejecutamos el serializer
                serializer_data[email_receiver].save()
                receiver_id = serializer_data[email_receiver].data["receiver"]
                if 'test' not in sys.argv:
                        # Envio de correos notificacion
                        mail = BasicEmailAmazon(subject=str(self.subject), to=email_receiver,
                                    template='email/empower')
                        if receiver is not None:
                            arguments = {'message':self.default_message, 'link':WEB_HOST}
                        else:
                            arguments = {'message':REGISTRATION_MESSAGE, 'link':REGISTER_LINK}

                        mail.sendmail(args=arguments)

                        if status_transfer == 1:
                            dict_pending = NotificationClientSerializer(qset_client).data
                            badge_count = dict_pending["queries_pending"] + dict_pending["match_pending"]
                            data_notif_push = {
                                "title": "Se te ha facultado un plan",
                                "body": display_client_name(client_obj),
                                "sub_text": "",
                                "ticker": "",
                                "badge": badge_count,
                                "icon": client_obj.photo,
                                "plan_id": acquired_plan.id,
                                "type": Params.TYPE_NOTIF["plan"],
                                "queries_pending": dict_pending["queries_pending"],
                                "match_pending": dict_pending["match_pending"]
                            }
                            # envio de notificacion push
                            Notification.fcm_send_data(user_id=receiver_id,
                                                       data=data_notif_push)
            return Response({})


class ClientTransferPlansView(APIView):
    """Vista para obetener todos los planes de un cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)
    required = _("required")
    default_message = _("Please click the next link to get your plan transfer")
    subject = _("Transfer Plan Success")
    invalid = _("invalid")
    already_exists = _("it already exists")

    def post(self, request):
        """Obtener la lista con todos los planes del cliente."""
        client = Operations.get_id(self, request)
        data = request.data

        if not 'acquired_plan' in data:
            raise serializers.ValidationError({'acquired_plan': [self.required]})

        if not 'email_receiver' in data:
            raise serializers.ValidationError({'email_receiver': [self.required]})

        # Traer al cliente
        try:
            sender = Client.objects.get(pk=client)
        except Client.DoesNotExist:
            raise Http404

        # Traer informacion del plan y de los permisos del plan
        try:
            acquired_plan = QueryPlansAcquired.objects.get(pk=data['acquired_plan'],
             queryplansclient__client=client, queryplansclient__transfer=True)
            acquired_plan_client = QueryPlansClient.objects.get(acquired_plan=acquired_plan,
             client=client)
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

        # Traemos a receptor si existe
        email_receiver = data['email_receiver']
        try:
            receiver = Client.objects.get(email_exact=email_receiver)
            status_transfer = 1
            qset_client = Client.objects.filter(pk=receiver.id)
        except Client.DoesNotExist:
            receiver = None
            status_transfer = 3

        checker = CheckEmailOperationPlan(1, email_receiver, acquired_plan, sender, receiver)
        if not checker.is_valid():
            raise serializers.ValidationError(checker.errors[0])

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
            'is_chosen': False,
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
        is_chosen_plan = acquired_plan_client.is_chosen
        serializer = QueryPlansTransferSerializer(data=data_transfer, context=data_context)

        if serializer.is_valid():
            if 'test' not in sys.argv:
                # Si el plan estaba escogido por el anterior cliente
                if is_chosen_plan:
                    pyrebase.delete_actual_plan_client(client)

                mail = BasicEmailAmazon(subject=str(self.subject), to=email_receiver,
                            template='email/transfer')
                if receiver is not None:
                    arguments = {'message':self.default_message, 'link':WEB_HOST}
                else:
                    arguments = {'message':REGISTRATION_MESSAGE, 'link':REGISTER_LINK}
                mail.sendmail(args=arguments)
                if status_transfer == 1:
                    dict_pending = NotificationClientSerializer(qset_client).data
                    badge_count = dict_pending["queries_pending"] + dict_pending["match_pending"]
                    data_notif_push = {
                        "title": "Se te ha transferido un plan",
                        "body": display_client_name(sender),
                        "sub_text": "",
                        "ticker": "",
                        "badge": badge_count,
                        "icon": sender.photo,
                        "plan_id": acquired_plan.id,
                        "type": Params.TYPE_NOTIF["plan"],
                        "queries_pending": dict_pending["queries_pending"],
                        "match_pending": dict_pending["match_pending"]
                    }
                    # envio de notificacion push
                    Notification.fcm_send_data(user_id=receiver.id,
                                               data=data_notif_push)
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
                'plan_name', 'queryplansclient__is_chosen', 'is_active', 'status',
                'validity_months', 'query_quantity', 'queries_to_pay', 'activation_date',
                'available_queries', 'expiration_date', 'queryplansclient__transfer',
                'queryplansclient__share', 'queryplansclient__empower', 'queryplansclient__owner'
                ).annotate(is_chosen=F('queryplansclient__is_chosen'),
                    price=F('sale_detail__price'),
                    sale=F('sale_detail__sale'),
                  is_fee=F('sale_detail__sale__is_fee')).order_by('-id')

            self.check_object_permissions(self.request, obj)
            return obj
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

    def get(self, request):
        """Obtener la lista con todos los planes del cliente."""
        client_id = request.user.id
        plan = self.get_object(client_id)

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
            print("error ActivationPlanView")
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




class CheckEmailOperationPlan(object):
    """clase para validar los movimientos de planes"""
    invalid = _("invalid")
    plan_previously_transferred = _("the plan was previously transferred for this user")
    already_exists_empower = _("Has already been empowered")
    already_exists_share = _("Has already been shared")

    can_not_be_share = _("it can not be share")
    can_not_be_empower = _("it can not be empower")
    can_not_be_transfer = _("it can not be transfer")

    cannot_share_yourself = _("you can not be shared by yourself")
    cannot_empower_yourself = _("you can not be empowered by yourself")
    cannot_transfer_yourself = _("you can not be transferred by yourself")


    def __init__(self, type_operation, email_receiver, acquired_plan, sender, receiver, count=None):
        """ """
        self.errors = []
        self.type_operation = type_operation
        self.email_receiver = email_receiver
        self.acquired_plan = acquired_plan
        self.sender = sender
        self.receiver = receiver
        self.count = count

    def is_valid(self):
        """Funtion is valid"""
        response = self.check_email(self.type_operation, self.email_receiver, self.acquired_plan,
                         self.sender, self.receiver, self.count)

        return response

    def check_email(self, type_operation, email_receiver, acquired_plan, sender, receiver, count):
        """
            type_operation: Int, numero de operacion
            email_receiver: Str, correo receptor
            acquired_plan: Int or Obj, plan a ser descontado
            sender: Obj, el cliente que vendera
            receiver: Int or Obj or None, el cliente que recive el plan
        """
        # Compartir con sigo mismo
        if email_receiver == sender.email_exact:
            if type_operation == 1:
                self.errors.append({'email_receiver': [self.cannot_transfer_yourself]})
            if type_operation == 2:
                self.errors.append({'email_receiver': [self.cannot_share_yourself]})
            if type_operation == 3:
                self.errors.append({'email_receiver': [self.cannot_empower_yourself]})

        if type_operation == 1:
            """Transferir"""
            # No realizar operacion si tiene operacioens previas para este plan
            plan_manage = QueryPlansManage.objects.filter(
                Q(receiver=receiver, status=1) | Q(email_receiver=email_receiver, status=3)).filter(
                acquired_plan=acquired_plan)

            if plan_manage:
                if plan_manage[0].type_operation == 3:
                    message_error  = "{} {}".format(self.already_exists_empower, self.can_not_be_transfer)
                    self.errors.append({'email_receiver': [message_error]})

                elif plan_manage[0].type_operation == 2:
                    message_error  = "{} {}".format(self.already_exists_share, self.can_not_be_transfer)
                    self.errors.append({'email_receiver': [message_error]})

                elif plan_manage[0].type_operation == 1:
                    # Solo se puede transferir 1 vez
                    self.errors.append({'email_receiver': [self.plan_previously_transferred]})

        if type_operation == 2:
            """Compartir"""

            # Se valida que enviaron la cantidad mayor a 0
            if count and count <= 0:
                errors[email_receiver] = {'count': [self.invalid]}

            # No realizar operacion si tiene operaciones previas para este plan
            plan_manage = QueryPlansManage.objects.filter(
                Q(receiver=receiver, status=1) | Q(email_receiver=email_receiver, status=3)).filter(
                acquired_plan=acquired_plan, type_operation=3)

            if plan_manage:
                message_error  = "{} {}".format(self.already_exists_empower, self.can_not_be_share)
                self.errors.append({'email_receiver': [message_error]})

        if type_operation == 3:
            """Facultar"""
            plan_manage = QueryPlansManage.objects.filter(
                Q(receiver=receiver, status=1) | Q(email_receiver=email_receiver, status=3)).filter(
                acquired_plan=acquired_plan)

            if plan_manage:
                if plan_manage[0].type_operation == 3:
                    message_error  = "{} {}".format(self.already_exists_empower, self.can_not_be_empower)
                    self.errors.append({'email_receiver': [self.already_exists_empower]})

                elif plan_manage[0].type_operation == 2:
                    message_error  = "{} {}".format(self.already_exists_share, self.can_not_be_empower)
                    self.errors.append({'email_receiver': [self.already_exists_share]})

        # Actualizacion de estatus valido
        if len(self.errors) > 0:
            return False
        else:
            return True

class ClientCheckEmailOperationView(APIView):
    """Vista para checkar si un correo puede realizar operacion"""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)
    required = _("required")

    def get(self, request):
        client_id = Operations.get_id(self, request)
        data = request.query_params

        response = {}
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
            sender = Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            raise serializers.ValidationError({'credentials': [self.invalid]})

        # Traer cliente by email si existe!
        try:
            receiver = Client.objects.get(email_exact=email_receiver)
        except Client.DoesNotExist:
            receiver = None

        checker = CheckEmailOperationPlan(type_operation, email_receiver, acquired_plan, sender, receiver)

        if not checker.is_valid():
            raise serializers.ValidationError(checker.errors[0])

        # Cliente no existe pero puede ser facultado, compartido, transferido
        if not receiver:
            raise Http404

        return Response(response)

class ClientDeleteEmpowerPlansView(ListCreateAPIView):
    """Vista para clientes Compartidos y facultados"""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)
    not_permission = _("You don't have permissions")
    required = _("required")

    # borrado
    def post(self, request):
        client = Operations.get_id(self, request)
        data = request.data
        if 'email_receiver' in data:
            email_receiver = data['email_receiver']
        else:
            raise serializers.ValidationError({'email_receiver': [self.required]})

        if 'acquired_plan' in data:
            acquired_plan = data['acquired_plan']
        else:
            raise serializers.ValidationError({'acquired_plan': [self.required]})

        client_plan = QueryPlansClient.objects.filter(client=client, acquired_plan=acquired_plan, empower=True)

        if client_plan:
            # El correo si movimientos a realizar
            query_manage = QueryPlansManage.objects.filter(email_receiver=email_receiver,
                acquired_plan=acquired_plan, type_operation=3)

            if query_manage:
                # Borramos referencias a ese cliente
                query_manage.delete()
                empower_obj = QueryPlansClient.objects.filter(client__email_exact=email_receiver,
                                    acquired_plan=acquired_plan)
                empower_obj.delete()

                #BORRAR DE PLAN CHOSEN FIREBASSE
            else:
                raise Http404

            return Response({})
        else:
            raise serializers.ValidationError({self.not_permission})

class ClientShareEmpowerPlansView(ListCreateAPIView):
    """Vista para clientes Compartidos y facultados"""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)

    def get(self, request, pk):
        client = Operations.get_id(self, request)
        data = request.data

        manage_data = QueryPlansManage.objects.values('email_receiver',
            'status','type_operation', 'receiver', 'new_acquired_plan'
            ).annotate(available_queries = F('new_acquired_plan__available_queries',),
            query_quantity = F('new_acquired_plan__query_quantity',),
            first_name = F('receiver__first_name',),
            last_name = F('receiver__last_name',),
            business_name = F('receiver__business_name',),
            type_client = F('receiver__type_client',),
            photo = F('receiver__photo',)).filter(
                Q(type_operation=2) | Q(type_operation=3)
                ).filter(acquired_plan = pk).distinct().order_by('-type_operation')

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


class PlansStatus(APIView):

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """Devolver Planes."""

        user_id = Operations.get_id(self, request)
        qs = QueryPlansAcquired.objects.filter(queryplansclient__client=user_id)
        # import pdb; pdb.set_trace()
        plans = PlanStatusSerializer(qs, context={"client": user_id})
        return Response(plans.data)


class PlansNonBillableSellerView(APIView):
    """Vista para crear planes no facturables."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsSeller)

    def get(self, request):
        """Devolver Planes."""
        duct = {}
        user_id = Operations.get_id(self, request)
        q_plans = QueryPlans.objects.filter(is_active=True,
                                            is_promotional=True)
        hoy = datetime.now()
        try:
            prom = SellerNonBillablePlans.objects.get(seller_id=user_id,
                                                      number_month=hoy.month,
                                                      number_year=hoy.year)
            duct["quantity"] = prom.quantity
        except SellerNonBillablePlans.DoesNotExist:
            duct["quantity"] = 0

        plans = QueryPlansSerializer(q_plans, many=True)
        duct["plans"] = plans.data
        return Response(duct)

class PlansNonBillableSellerByContactView(APIView):
    """Vista para crear planes no facturables."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsSeller)
    affirmative = _("affirmative")
    denied = _("denied")

    def get(self, request, pk):
        """Devolver Planes."""
        duct = {}
        user_id = Operations.get_id(self, request)
        result = self.can_receive_contact(user_id, pk)

        if result:
            return Response({"status": self.affirmative}, status.HTTP_200_OK)
        else:
            return Response({"status": self.denied}, status.HTTP_400_BAD_REQUEST)

    def can_receive_contact(self, seller_id, contact_id):
        hoy = datetime.now()
        try:
            prom = SellerNonBillablePlans.objects.get(seller_id=seller_id,
                                                      number_month=hoy.month,
                                                      number_year=hoy.year)
            quantity = prom.quantity
        except SellerNonBillablePlans.DoesNotExist:
            quantity = 0


        promitionals = SellerContact.objects.filter(pk=contact_id,
                                client__sale__saledetail__is_billable=False)
        
        if quantity>0 and not promitionals:
            # disponible de regalar y contacto no tiene promocionales
            return True
        else:
            return False
