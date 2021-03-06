"""Vista de todos los Actores."""
# from api.logger import manager

from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from rest_framework.generics import ListAPIView
from api.models import User, Client, Specialist, Seller, Query, ContactVisit
from api.models import SellerContact, SpecialistMessageList, SpecialistMessageList_sp
from api.models import RecoveryPassword, Declinator, QueryPlansManage, Parameter
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, generics
from rest_framework import serializers
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.db.models import OuterRef, Subquery, Q, Sum
from django_filters import rest_framework as filters
from rest_framework import filters as searchfilters
from api.serializers.actors import ClientSerializer, UserPhotoSerializer, ClientDetailSerializer
from api.serializers.actors import KeySerializer, ContactPhotoSerializer
from api.serializers.actors import UserSerializer, SpecialistSerializer
from api.serializers.actors import SellerContactSerializer
from api.serializers.actors import AssociateSpecialistSerializer
from api.serializers.actors import SellerContactNaturalSerializer
from api.serializers.actors import SellerFilterContactSerializer
from api.serializers.actors import SellerSerializer, SellerContactBusinessSerializer
from api.serializers.actors import MediaSerializer, ChangePasswordSerializer, SpecialistMessageListCustomSerializer
from api.serializers.actors import ChangeEmailSerializer, ChangePassword
from api.serializers.actors import ObjectionsContactSerializer
from api.serializers.payment import ContactVisitSerializer
from api.serializers.query import QuerySerializer, QueryCustomSerializer
from api.serializers.plan import QueryPlansShareSerializer, QueryPlansTransferSerializer
from api.serializers.plan import QueryPlansEmpowerSerializer
from django.http import Http404
from django.db.models import Count

from api.permissions import IsAdminOnList, IsAdminOrOwner, IsSeller, IsAdminOrSpecialist, IsAdminOrSeller
from api.permissions import IsAdminOrClient

from api.utils.querysets import get_query_set_plan
from rest_framework.parsers import JSONParser, MultiPartParser, FileUploadParser
from django.utils.translation import ugettext_lazy as _
import os
import uuid
import boto3, sys
import random, string

from datetime import datetime, date, timedelta
from django.utils import timezone
from api.utils.validations import Operations
from api.utils.tools import clear_data_no_valid
from api.utils.functions import generate_seller_goals

from api import pyrebase
from api.emails import BasicEmailAmazon
from api.utils.parameters import Params
from api.api_choices_models import ChoicesAPI as c
from api.logger import manager
logger = manager.setup_log(__name__)

# Constantes
PREFIX_CODE_CLIENT = 'C'
ROLE_CLIENT = 2
ROLE_SPECIALIST = 3
ROLE_SELLER = 4
PREFIX_CODE_SPECIALIST = 'E'
PREFIX_CODE_SPECIALIST_ASSOCIATE = 'EA'
PREFIX_CODE_SELLER = 'V'
DATE_FAKE = '1900-01-01'
# Fin de constantes

#obtener el logger con la configuracion para actors
# loggerActor = manager.setup_log(__name__)


class UpdateUserPassword(APIView):
    """Actualizar contraseña de Usuario."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrOwner)

    def get_object(self, pk):
        """Devolver objeto."""
        try:
            obj = User.objects.get(pk=pk)
            return obj
        except User.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Funcion put."""
        data = request.data
        user = self.get_object(pk)
        serializer = ChangePassword(user, data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    """Actualizar Contraseña de Usuario (uso para dev)."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk):
        """Devolver objeto."""
        try:
            obj = User.objects.get(pk=pk)
            return obj
        except User.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Funcion put."""
        data = request.data
        user = self.get_object(pk)
        serializer = ChangePasswordSerializer(user, data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendCodePassword(APIView):
    """Actualizar Contraseña de Usuario (uso para dev)."""
    required = _("required")
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk):
        """Devolver objeto."""
        try:
            obj = User.objects.get(pk=pk)
            return obj
        except User.DoesNotExist:
            raise Http404

    def post(self, request):
        """Funcion put."""
        if 'email' in request.data:
            email = request.data["email"]
        else:
            raise serializers.ValidationError({'email': [self.required]})

        user_filter = User.objects.filter(email_exact=email)

        if not user_filter:
            raise Http404

        user = self.get_object(user_filter)
        recovery_password = RecoveryPassword()
        recovery_password.user = user
        recovery_password.code = code = tools.ramdon_generator(6)
        recovery_password.is_active = True
        recovery_password.save()

        if 'test' not in sys.argv:
            data = {'code':code}
            mail = BasicEmailAmazon(subject="Codigo de cambio de contraseña",
                to=email, template='email/send_code')
            response = mail.sendmail(args=data)
        else:
            response = None
        return Response(response)

class ValidCodePassword(APIView):
    """Actualizar Contraseña de Usuario (uso para dev)."""
    required = _("required")
    invalid = _("not valid")
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Funcion put."""
        if 'code' in request.query_params:
            code = request.query_params["code"]
        else:
            raise serializers.ValidationError({'code': [self.required]})

        if 'email' in request.query_params:
            email = request.query_params["email"]
        else:
            raise serializers.ValidationError({'email': [self.required]})

        user_filter = User.objects.filter(recoverypassword__code=code, email_exact=email, is_active=True).extra(where = ["DATEDIFF(NOW() ,created_at )<=1"])
        # print(user_filter.query)
        if user_filter:
            user = User.objects.get(pk=user_filter)
            user_serializer = UserSerializer(user, partial=True)
            return Response(user_serializer.data)
        else:
            raise Http404

class UpdatePasswordRecoveryView(APIView):
    """Actualizar Contraseña de Usuario Recuperado."""
    required = _("required")
    invalid = _("not valid")
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk):
        """Devolver objeto."""
        try:
            obj = User.objects.get(pk=pk)
            return obj
        except User.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Funcion put."""
        if 'code' in request.data:
            code = request.data["code"]
        else:
            raise serializers.ValidationError({'code': [self.required]})

        user_filter = RecoveryPassword.objects.filter(code=code, user=pk, is_active=True).extra(where = ["DATEDIFF(NOW() ,created_at )<=1"])

        if user_filter:
            data = request.data
            user = self.get_object(pk)
            serializer = ChangePasswordSerializer(user, data, partial=True)
            if serializer.is_valid():
                serializer.save()

                recovery = RecoveryPassword.objects.get(pk=user_filter)
                recovery.is_active = False
                recovery.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise Http404

    def get(self, request):

        user = self.get_object(user_filter)
        user.password = True
        user.save()

        if user_filter:
            return Response({})
        else:
            raise serializers.ValidationError({'code': [self.invalid]})

class UpdatePasswordUserView(APIView):
    """Actualizar Contraseña de Usuario Recuperado."""
    required = _("required")
    invalid = _("not valid")
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrOwner)

    def get_object(self, pk):
        """Devolver objeto."""
        try:
            obj = User.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except User.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Funcion put."""
        data = request.data
        user = self.get_object(pk)
        serializer = ChangePasswordSerializer(user, data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)




class UpdateEmailUserView(APIView):
    """Actualizar Contraseña de Usuario Recuperado."""
    required = _("required")
    invalid = _("not valid")
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrOwner)

    def get_object(self, pk):
        """Devolver objeto."""
        try:
            obj = User.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except User.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Funcion put."""
        data = request.data
        pk = Operations.get_id(self, request)
        user = self.get_object(pk)
        last_email = user.email_exact
        serializer = ChangeEmailSerializer(user, data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Actualizamos Email si existe en el manejo de planes
            plan_manages = QueryPlansManage.objects.filter(email_receiver=last_email)
            if plan_manages:
                success = plan_manages.update(email_receiver=data['email_exact'])

            seller_contact = SellerContact.objects.filter(email_exact=last_email)
            if seller_contact:
                success = seller_contact.update(email_exact=data['email_exact'])

            return Response(serializer.data)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)



class ViewKey(APIView):
    """Devuelve la contraseña sin encriptar (uso exclusivo para dev)."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk):
        """Obtener objeto."""
        try:
            obj = User.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """Detalle."""
        user = self.get_object(pk)
        serializer = KeySerializer(user)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Vista para traer datos de usuarios (Logueo en la web)."""

    authentication_classes = (OAuth2Authentication,)
    # solo el admin puede consultar
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('username',)


from api.models import QueryPlansAcquired, SaleDetail, Sale, QueryPlansClient
from api.models import Clasification, QueryPlans, ProductType
from api.utils import tools
from api.pyrebase import chosen_plan
from api.serializers.plan import QueryPlansAcquiredSerializer

def give_plan_new_client(client_id, is_chosen = True):
    """OJO."""
    """FUNCION CREADA PARA OTORGAR PLANES A CLIENTES NUEVOS"""
    """ESTA FUNCION DEBE SER BORRADA DESPUES DE TENER EL MODULO DE COMPRAS"""
    sale = Sale()
    saleDetail = SaleDetail()
    queryPlansAcquired = QueryPlansAcquired()
    queryPlansClient = QueryPlansClient()

    try:
        product_type = ProductType.objects.get(pk=1)
    except Exception as e:
        product_type = ProductType()
        product_type.name = 'Plan Query'
        product_type.id = '1'
        product_type.save()

    try:
        clasification = Clasification.objects.get(pk=1)
    except Exception as e:
        clasification = Clasification()
        clasification.name = 'TesterType'
        clasification.id = '1'
        clasification.save()

    try:
        query_plans = QueryPlans.objects.get(pk=3)
    except Exception as e:
        query_plans = QueryPlans()
        query_plans.product_type = product_type
        query_plans.clasification = clasification
        query_plans.id = 1
        query_plans.query_quantity = 6
        query_plans.validity_months = 3
        query_plans.maximum_response_time = 24
        query_plans.is_active = 1
        query_plans.price = 900
        query_plans.name = 'MiniPack'
        query_plans.save()

    sale.created_at = datetime.now()
    sale.place = 'BCP'
    sale.total_amount = query_plans.price
    sale.reference_number = 'CD1004'
    sale.description = 'Test Venta'
    sale.is_fee = False
    sale.client_id = client_id
    sale.save()

    saleDetail.price = query_plans.price
    saleDetail.description = 'Plan de Prueba'
    saleDetail.discount = '0.00'
    saleDetail.pin_code = tools.ramdon_generator(6)
    saleDetail.is_billable = True
    saleDetail.contract_id = None
    saleDetail.product_type_id = product_type.id
    saleDetail.sale_id = sale.id
    saleDetail.save()

    queryPlansAcquired.expiration_date = '2019-04-09'
    queryPlansAcquired.validity_months = query_plans.validity_months
    queryPlansAcquired.available_queries = query_plans.query_quantity
    queryPlansAcquired.queries_to_pay = 0
    queryPlansAcquired.activation_date = datetime.now()
    queryPlansAcquired.is_active = True
    queryPlansAcquired.available_requeries = 1
    queryPlansAcquired.maximum_response_time = query_plans.maximum_response_time
    queryPlansAcquired.acquired_at = datetime.now()
    queryPlansAcquired.query_plans_id = query_plans.id
    queryPlansAcquired.sale_detail_id = saleDetail.id
    queryPlansAcquired.query_quantity = query_plans.query_quantity
    queryPlansAcquired.plan_name = query_plans.name
    queryPlansAcquired.save()

    queryPlansClient.owner = True
    queryPlansClient.transfer = True
    queryPlansClient.share = True
    queryPlansClient.empower = True
    queryPlansClient.status = 1
    queryPlansClient.acquired_plan_id = queryPlansAcquired.id
    queryPlansClient.client_id = client_id
    queryPlansClient.is_chosen = is_chosen
    queryPlansClient.save()

    plan_chosen = get_query_set_plan()
    plan_active = plan_chosen.filter(queryplansclient__client=client_id, is_active=True,
                                             queryplansclient__is_chosen=True)
    serializer = QueryPlansAcquiredSerializer(plan_active[0])
    chosen_plan(client_id, serializer.data)

# Vista para Listar y Crear Clientes
class ClientListView(ListCreateAPIView):
    """Vista Cliente."""

    required = _("required")
    # Lista todos los clientes naturales o crea uno nuevo
    # no olvidar lo de los permisos
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAdminOnList,)
    # permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    filter_backends = (filters.DjangoFilterBackend, searchfilters.SearchFilter,)
    filter_fields = ('nick',)
    search_fields = ('email_exact', 'first_name')

    # Metodo post redefinido
    def post(self, request):
        """Ahora se usa el post de ContactListView"""

        view = ContactListView()
        return view.post(request)
        """Redefinido metodo para crear clientes."""
        # data = request.data
        # if 'type_client' not in data or not data['type_client']:
        #     raise serializers.ValidationError({'type_client': [self.required]})

        # # generamos contraseña random
        # if 'register_type' in data and data['register_type'] == 2:
        #     password = ''.join(random.SystemRandom().choice(string.digits) for _ in range(6))
        #     data["password"] = password

        # if data['type_client'] == 'n':
        #     data['economic_sector'] = ''
        # elif data['type_client'] == 'b':
        #     data['birthdate'] = DATE_FAKE
        #     data['sex'] = ''
        #     data['civil_state'] = ''
        #     data['level_instruction'] = ''
        #     data['profession'] = ''
        #     data['ocupation'] = None
        # data['role'] = ROLE_CLIENT
        # serializer = ClientSerializer(data=data)
        # if serializer.is_valid():
        #     serializer.save()

        #     if 'test' not in sys.argv:
        #         # se le crea la lista de todas las categorias al cliente en firebase
        #         pyrebase.createCategoriesLisClients(serializer.data['id'])

        #         if 'register_type' in data and data['register_type'] == 2:
        #             # envio de contraseña al cliente
        #             mail = BasicEmailAmazon(subject='Envio Credenciales', to=data["email_exact"],
        #                                     template='email/send_credentials')
        #             credentials = {}
        #             credentials["user"] = data["email_exact"]
        #             credentials["pass"] = password
        #             mail.sendmail(args=credentials)

        #     # FUNCION TEMPORAL PARA OTORGAR PLANES A CLIENTES
        #     # give_plan_new_client(serializer.data['id']) # OJO FUNCION TEMPORAL

        #     client_id = serializer.data['id']
        #     email = data['email_exact']
        #     self.check_plans_operation_manage(client_id, email)

        #     return Response(serializer.data, status.HTTP_201_CREATED)
        # return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def check_plans_operation_manage(self, receiver_id, email_receiver):
        """
            funcion creada para otorgar al cliente beneficios segun su corre
            de registro
        """
        # No realizar operacion si tiene operacioens previas para este plan
        plan_manages = QueryPlansManage.objects.filter(
            email_receiver=email_receiver, status=3)
        receiver = Client.objects.get(pk=receiver_id)

        for plan_manage in plan_manages:
            """Checar y otorgar planes a nuevo cliente"""
            data = {
                'receiver': receiver_id,
                'status': 1,
                'count_queries': plan_manage.count_queries
            }

            data_context = {}
            if plan_manage.type_operation == 2:

                data_context['client_receiver'] = {
                    'is_chosen': False,
                    'owner': False,
                    'transfer': False,
                    'share': False,
                    'empower': False,
                    'status': 1,
                    'acquired_plan': None,
                    'client': receiver
                }
                data_context['count'] = plan_manage.count_queries
                data_context['acquired_plan'] = plan_manage.acquired_plan
                data_context['plan_manage'] = None

                serializer = QueryPlansShareSerializer(plan_manage, data, partial=True,
                                              context=data_context)

            elif plan_manage.type_operation == 1:
                # Transferir plan de consultas
                data_context['client_receiver'] = {
                    'is_chosen': False,
                    'owner': True,
                    'transfer': False,
                    'share': True,
                    'empower': True,
                    'status': 1,
                    'acquired_plan': plan_manage.acquired_plan,
                    'client': receiver
                }
                serializer = QueryPlansTransferSerializer(plan_manage, data, partial=True,
                                              context=data_context)

            elif plan_manage.type_operation == 3:
                # Facultar plan de consultas
                data_context['client_receiver'] = {
                    'is_chosen': False,
                    'owner': False,
                    'transfer': False,
                    'share': True,
                    'empower': False,
                    'status': 1,
                    'acquired_plan': plan_manage.acquired_plan,
                    'client': receiver
                }
                serializer = QueryPlansEmpowerSerializer(plan_manage, data, partial=True,
                                              context=data_context)

            else:
                continue

            if serializer.is_valid():
                serializer.save()

# Vista para Detalle del Cliente
class ClientDetailView(APIView):
    """Detalle del Cliente, GET/PUT/Delete."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # permission_classes = [permissions.IsAuthenticated, TokenHasScope]

    def get_object(self, pk):
        """Obtener objeto."""
        try:
            obj = Client.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except Client.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """Detalle."""
        client = self.get_object(pk)
        serializer = ClientSerializer(client)
        return Response(serializer.data)

    def put(self, request, pk):
        """Detalle."""
        client = self.get_object(pk)
        data = request.data

        valid_fields = ("commercial_reason", "ciiu", "nick",
                "telephone", "cellphone", "code_telephone", "code_cellphone", "residence_country", "address", "foreign_address")

        clear_data_no_valid(data, valid_fields)

        serializer = ClientSerializer(client, data, partial=True,
                                          context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para detalle del cliente segun su username
# se hizo con la finalidad de instanciar una vez logueado
class ClientDetailByUsername(APIView):
    """Traer detalle del cliente por nombre de usuario."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, username):
        """Obtener objeto si existe."""
        try:
            client = Client.objects.get(username=username)
            return client
        except Client.DoesNotExist:
            raise Http404

    def get(self, request, username):
        """Devuelve Cliente."""
        client = self.get_object(username)
        serializer = ClientSerializer(client)
        return Response(serializer.data)


# Fin de Clientes

# ---------- ------ Inicio de Especialistas ------------------------------

# Vista para detalle del cliente segun su username
# se hizo con la finalidad de instanciar una vez logueado
class SpecialistDetailByUsername(APIView):
    """Detalle de Especialista por Nombre de Usuario."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, username):
        """Obtener Objeto."""
        try:
            return Specialist.objects.get(username=username)
        except Specialist.DoesNotExist:
            raise Http404

    def get(self, request, username):
        """Obtener Especialista."""
        specialist = self.get_object(username)
        serializer = SpecialistSerializer(specialist, context={'request': request})
        return Response(serializer.data)


class SpecialistQueryCountView(ListCreateAPIView):
    authentication_classes = (OAuth2Authentication,)
    # permission_classes = (permissions.IsAuthenticated,)
    # usando la nueva validacion de permisos
    permission_classes = (IsAdminOrSpecialist,)

    def get_count(self, specialist_id, fecha_init, fecha_end, request):
        """Obtener entero resultado del total de registros encontrados."""
        try:
            count = Query.objects.filter(specialist_id=specialist_id, changed_on__range=(fecha_init, fecha_end)).count()
            self.check_object_permissions(self.request, count)
            return count
        except Query.DoesNotExist:
            raise Http404

    def get(self, request):
        """Obtener numero de consultas del especialista."""
        data = {}
        specialist_id = request.user.id
        # now2 = datetime.utcnow()
        # se obtiene el current timestamp utc
        now = timezone.now()
        # first_day_month = date(now.year,now.month,1)
        # first_day_year = date(now.year, 1, 1)
        # se arma las fechas -> primer dia del mes actual y primer dia del año actual
        first_day_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        first_day_year = datetime(now.year, 1, 1, tzinfo=timezone.utc)
        month_count = self.get_count(specialist_id, first_day_month, now, request)
        year_count = self.get_count(specialist_id, first_day_year, now, request)

        data['specialist_id'] = specialist_id
        data['month_count'] = month_count
        data['year_count'] = year_count

        serializer = QueryCustomSerializer(data)
        return Response(serializer.data)
        # return Response(JSONRenderer().render(respuesta), status=200)


class SpecialistListView(ListCreateAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer

    # funcion para localizar especialista principal
    def get_object(self, pk):
        try:
            return Specialist.objects.get(pk=pk, type_specialist='m')
        except Specialist.DoesNotExist:
            raise Http404

    # Funcion personalizada para
    # devolver los especialistas asociados a un principal si envian el
    # parametro [main_specialist]
    def list(self, request):
        # en dado caso que exista el parametro "main_specialist", se devuelve
        # el listado de especialistas asociados, caso contrario devuelve todos

        if 'main_specialist' in request.query_params:
            specialist = self.get_object(
                request.query_params["main_specialist"])
            queryset = Specialist.objects.filter(
                category_id=specialist.category).exclude(type_specialist='m')
            serializer = SpecialistSerializer(queryset, many=True,
                                              context={'request': request})
        else:
            queryset = self.get_queryset()
            serializer = SpecialistSerializer(queryset, many=True,
                                              context={'request': request})

        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    # Funcion para crear un especialista
    def post(self, request):
        """Redefinido funcion para crear especialista."""
        required = _("required")
        data = request.data
        # codigo de usuario se crea con su prefijo de especialista y su numero de documento
        if "document_number" not in data:
            raise serializers.ValidationError({'document_number': [required]})

        if request.data.get("type_specialist") == "m":
            data['code'] = PREFIX_CODE_SPECIALIST + request.data.get('document_number')
        else:
            data['code'] = PREFIX_CODE_SPECIALIST_ASSOCIATE + request.data.get('document_number')

        data['role'] = ROLE_SPECIALIST
        serializer = SpecialistSerializer(
            data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpecialistAsociateListView(ListCreateAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSpecialist)

    def get(self, request):
        pk = Operations.get_id(self, request)

        try:
            obj = Specialist.objects.get(pk=pk, type_specialist='m')
        except Specialist.DoesNotExist:
            raise Http404

        specialists = Specialist.objects.filter(category=obj.category,
                                                type_specialist="a")

        page = self.paginate_queryset(specialists)
        if page is not None:
            serializer = AssociateSpecialistSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = AssociateSpecialistSerializer(specialists, many=True)
        return Response(serializer.data)


class SpecialistAsociateListByQueryView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSpecialist)
    required = _("required")

    def get(self, request):
        pk = Operations.get_id(self, request)
        if 'query' in request.query_params:
            query = request.query_params["query"]
        else:
            raise serializers.ValidationError({'query': [self.required]})

        try:
            obj = Specialist.objects.get(pk=pk)
        except Specialist.DoesNotExist:
            raise Http404

        declined = Declinator.objects.filter(specialist=OuterRef('pk'), query= query)

        specialists = Specialist.objects.filter(category=obj.category, type_specialist="a")\
                        .annotate(declined=Subquery(declined.values('specialist')[:1]))

        serializer = SpecialistSerializer(specialists, many=True)
        return Response(serializer.data)

class PutSpecialistMessages():
    def get(self, pk):
        obj = SpecialistMessageList.objects.filter(client=pk)
        serializer = SpecialistMessageListCustomSerializer(obj, many=True)
        return serializer.data


class SpecialistMessagesListView(ListCreateAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAdminOrSpecialist,)

    def get_object(self, pk):
        try:
            # se le manda 1 en el primer parametro para que el SP realice el filtro por especialista
            obj = SpecialistMessageList_sp.search(1, pk, 0, 0, "")
            self.check_object_permissions(self.request, obj)
            return obj
        except SpecialistMessageList.DoesNotExist:
            raise Http404

    # listado
    def list(self, request):
        # obtengo el pk del especialista
        pk = Operations.get_id(self, request)
        list = self.get_object(pk)
        serializer = SpecialistMessageListCustomSerializer(list, many=True)

        page = self.paginate_queryset(list)
        if page is not None:
            serializer = SpecialistMessageListCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


# Vista para el detalle del especialista, actualizacion y borrado
class SpecialistDetailView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAdminOrSpecialist,)

    def get_object(self, pk):
        try:
            obj = Specialist.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except Specialist.DoesNotExist:
            raise Http404

    # detalle
    def get(self, request, pk):
        specialist = self.get_object(pk)
        serializer = SpecialistSerializer(
            specialist, context={'request': request})
        return Response(serializer.data)

    # actualizacion
    def put(self, request, pk):
        """Actualizar."""
        data = request.data
        specialist = self.get_object(pk)
        # codigo de usuario se crea con su prefijo de especialista y su numero de documento

        if request.data.get("type_specialist") == "m":
            data['code'] = PREFIX_CODE_SPECIALIST + request.data.get(
                'document_number', specialist.document_number)
        else:
            data['code'] = PREFIX_CODE_SPECIALIST_ASSOCIATE + request.data.get(
                'document_number', specialist.document_number)

        data['photo'] = request.data.get('photo', specialist.photo)
        data['username'] = specialist.username
        data['role'] = ROLE_SPECIALIST

        serializer = SpecialistSerializer(specialist, data, partial=True,
                                          context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # borrado
    def delete(self, request, pk):
        specialist = self.get_object(pk)
        specialist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# ------------ Fin de Especialistas -----------------


# ---------- ------ Inicio de Vendedores ------------------------------

class SellerFilter(filters.FilterSet):
    count_plans_seller = filters.NumberFilter(name='count_plans_seller', method='filter_count_plans')
    count_queries_seller = filters.NumberFilter(name='count_queries_seller', method='filter_count_queries')

    def filter_count_plans(self, qs, name, value):
        # todos los id de vendedores que han vendido mas que value
        sellers_ids = []
        for seller in Seller.objects.all():
            # calcular cantidad vendida
            count = Purchase.objects.filter(seller=seller.id).count()
            # si la cantidad vendida es mayor que el parametro
            # agregar a la lista
            if count > value:
                sellers_ids.append(seller.id)
        return qs.filter(id__in=sellers_ids)

    def filter_count_queries(self, qs, name, value):
        # todos los id de vendedores que han vendido mas que value
        sellers_ids = []
        for seller in Seller.objects.all():
            # calcular cantidad vendida
            count_result = Product.objects.filter(purchase__seller__isnull=False, purchase__seller=seller.id).aggregate(
                Sum('query_amount'))
            count = count_result['query_amount__sum']
            # si la cantidad vendida es mayor que el parametro
            # agregar a la lista
            if count and count > value:
                sellers_ids.append(seller.id)
        return qs.filter(id__in=sellers_ids)

    first_name = filters.CharFilter(name='first_name', lookup_expr='icontains')
    last_name = filters.CharFilter(name='last_name', lookup_expr='icontains')
    ruc = filters.CharFilter(name='ruc', lookup_expr='icontains')
    email_exact = filters.CharFilter(name='email_exact', lookup_expr='icontains')

    class Meta:
        model = Seller
        fields = ['first_name', 'last_name', 'ruc', 'email_exact']


class SellerListView(ListCreateAPIView, UpdateAPIView):
    """Vista de Listado y Creacion Vendedores."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAdminUser,)
    # permission_classes = [permissions.AllowAny]
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = SellerFilter

    # Funcion para crear un especialista
    def post(self, request):
        """Redefinido funcion para crear vendedor."""
        required = _("required")
        data = request.data
        # codigo de usuario se crea con su prefijo de especialista y su numero de documento
        if "document_number" not in data:
            raise serializers.ValidationError({'document_number': [required]})
        data['code'] = PREFIX_CODE_SELLER + request.data.get('document_number')
        data['role'] = ROLE_SELLER
        serializer = SellerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            generate_seller_goals(serializer.data['id'])

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellerClientListView(ListCreateAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSeller)

    def list(self, request):

        seller = Operations.get_id(self, request)

        clients = Client.objects.filter(sellercontact__type_contact=3).distinct()

        # Filtro de tipo de clientes (Mis clientes/Asignados)
        # assignment_type = 1 (Mis clientes)
        # assignment_type = 2 (Mis asignados)
        assignment_type = self.request.query_params.get('assignment_type', '1')
        if assignment_type is not None:
            if int(assignment_type) == 1:
                clients = clients.filter(sellercontact__is_assigned=False)
            elif int(assignment_type) == 2:
                clients = clients.filter(sellercontact__is_assigned=True)

        # Filtro fecha desde y fecha hasta
        date_start = self.request.query_params.get('date_start', None)
        date_end = self.request.query_params.get('date_end', None)
        if date_start is not None and date_end is not None:
            fecha_end = datetime.strptime(date_end, '%Y-%m-%d')
            date_end = fecha_end + timedelta(days=1)
            clients = clients.filter(date_joined__range=(date_start, date_end)).distinct()

        # Filtro de clientes con consultas disponibles
        # available = 1 (Los clientes que tienen planes con consultas disponibles)
        # available = 2 (Los clientes sin planes con consultas disponibles)
        available = self.request.query_params.get('available', None)
        if available is not None :
            qpc = QueryPlansClient.objects.filter(client__in=clients,
                                                  acquired_plan__available_queries__gt=0,
                                                  acquired_plan__is_active=True).distinct()

            if int(available) == 1:
                clients = clients.filter(queryplansclient__in=qpc).distinct()
            elif int(available) == 2:
                clients = clients.exclude(queryplansclient__in=qpc).distinct()


        serializer = ClientSerializer(clients, many=True)
        # pagination
        page = self.paginate_queryset(clients)
        if page is not None:
            serializer = ClientSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

class AssignClientToOtherSeller(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSeller]

    def get_object(self, pk):
        try:
            obj = Client.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except Client.DoesNotExist:
                raise Http404

    def put(self, request, pk):
        data = request.data

        client = self.get_object(pk)

        updated_data = {}
        updated_data['seller_assigned'] = request.data['seller_id']

        serializer = ClientDetailSerializer(client, updated_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellerDetailView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Seller.objects.get(pk=pk)
        except Seller.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        seller = self.get_object(pk)
        serializer = SellerSerializer(seller)
        return Response(serializer.data)

    def put(self, request, pk):
        data = request.data

        seller = self.get_object(pk)
        # codigo de usuario se crea con su prefijo de especialista y su numero de documento
        data['code'] = PREFIX_CODE_SELLER + request.data.get('document_number', seller.document_number)
        data['photo'] = request.data.get('photo', seller.photo)
        data['username'] = seller.username
        data['role'] = ROLE_SELLER

        serializer = SellerSerializer(seller, data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellerDetailByUsername(APIView):
    """Detalle de Vendedor por Nombre de Usuario."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, username):
        """Obtener Objeto."""
        try:
            return Seller.objects.get(username=username)
        except Seller.DoesNotExist:
            raise Http404

    def get(self, request, username):
        """Obtener Vendedor."""
        seller = self.get_object(username)
        serializer = SellerSerializer(seller)
        return Response(serializer.data)

class SellerDetailByID(APIView):
    """Detalle de Vendedor por Nombre de Usuario."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        """Obtener Objeto."""
        try:
            return Seller.objects.get(pk=pk)
        except Seller.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """Obtener Vendedor."""
        seller = self.get_object(pk)
        serializer = SellerSerializer(seller)
        return Response(serializer.data)


# class SellerAccountView(ListCreateAPIView):
#     authentication_classes = (OAuth2Authentication,)
#     permission_classes = (permissions.IsAdminUser,)

#     def get_object(self, pk):
#         try:
#             return Specialist.objects.get(pk=pk)
#         except Specialist.DoesNotExist:
#             raise Http404

    # def get(self, request, pk):
    #     creacion de QuerySet para listadaos
    #     queryset = Seller.objects.filter(id=pk,purchase__fee__status=1)\
    #         .values('id','purchase__total_amount',
    #                               'purchase__id','purchase__code','purchase__query_amount','purchase__fee_number',
    #                               'purchase__product__is_billable','purchase__product__expiration_number','purchase__product__name',
    #                               'purchase__client__code','purchase__client__nick', 'purchase__fee__date', 'purchase__fee__id',
    #                               'purchase__fee__fee_amount','purchase__fee__status','purchase__fee__payment_type__name',
    #                               'purchase__fee__reference_number','purchase__fee__fee_order_number',
    #                               )\
    #         .order_by('purchase__fee__date')
    #
    #     serializer = SellerAccountSerializer(queryset, many=True)
    #     # pagination
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     return Response(serializer.data)

class ContactVisitListView(ListCreateAPIView):
    authentication_classes = (OAuth2Authentication,)

    def get(self, request, pk):
        type_visit = request.query_params.get('type_visit', None)
        visits = ContactVisit.objects.filter(contact=pk).order_by("-created_at")

        if type_visit:
            visits = visits.filter(type_visit=type_visit)

        page = self.paginate_queryset(visits)
        if page is not None:
            serializer = ContactVisitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ContactVisitSerializer(specialists, many=True)
        return Response(serializer.data)


class ContactVisitNoEffectiveView(APIView):

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSeller)
    required = _("required")

    def post(self, request, pk):
        data = dict(request.data)
        seller = Operations.get_id(self, request)

        if 'other_objection' in data:
            other_objection = data["other_objection"]
        else:
            other_objection = None

        data["seller"] = seller
        data["contact"] = pk
        data["type_visit"] = 2
        data["other_objection"] = other_objection

        serializer = ContactVisitSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        # if "other_objection" in validated_data:
        #         other_objection = validated_data["other_objection"]
        #     else:
        #         other_objection = None

        #     visit_instance = ContactVisit.objects.create(contact=instance,
        #                             type_visit=validated_data["type_contact"],
        #                             latitude=validated_data["latitude"],
        #                             longitude=validated_data["longitude"],
        #                             other_objection=other_objection,
        #                                 seller=instance.seller)
        #     if 'objection_list' in locals():
        #         for objection in objection_list:
        #             # objection_obj = Objection.objects.get(pk=objection)
        #             ObjectionsList.objects.create(contact=instance,
        #                                          contact_visit=visit_instance,
        #                                           objection=objection)


class ContactVisitUpdate(APIView):

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSeller)
    required = _("required")

    def get_object(self, pk):
        """Obtener Objeto."""

        try:
            visit = ContactVisit.objects.get(pk=pk)
            return visit
        except ContactVisit.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        data = dict(request.data)

        visit = self.get_object(pk)

        if 'other_objection' in data:
            data["other_objection"] = visit.other_objection + '\n' + data["other_objection"]

        serializer = ContactVisitSerializer(visit, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors, HTTP_400_BAD_REQUEST)


class ContactListView(ListCreateAPIView):
    """Vista para Contacto No Efectivo."""

    authentication_classes = (OAuth2Authentication,)
    # aca se debe colocar el serializer para listar todos
    serializer_class = SellerContactNaturalSerializer
    queryset = SellerContact.objects.all()

    def get(self, request):
        """Devolver contactos del vendedor."""
        seller = Operations.get_id(self, request)

        if not seller:
            response = {
                "detail": "Las credenciales de autenticación no se proveyeron."
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

        date_start = self.request.query_params.get('date_start', None)
        date_end = self.request.query_params.get('date_end', None)
        assignment_type = int(self.request.query_params.get('assignment_type', '1'))
        today = datetime.today()

        # Filters
        if date_end:
            date_end = datetime.strptime(date_end, '%Y-%m-%d')
            date_end = date_end + timedelta(days=1)
        else:
            date_end = today + timedelta(days=1)
            date_end = date_end.strftime('%Y-%m-%d')

        if date_start is None:
            date_start = today.strftime('%Y-%m-%d')

        if assignment_type and assignment_type == 2: # Mis Asignados
            is_assigned = 1
        else:
            is_assigned = 0

        contacts = SellerContact.objects.raw("""
                SELECT DISTINCT
                IF (
                    se.type_contact = 4,
                    se.type_contact,
                    IF (
                        se.type_contact = 1
                        AND (
                            SELECT
                                sale.id
                            FROM
                                api_sale AS sale
                            WHERE
                                sale.file_url <> ""
                            LIMIT 1
                        ),
                        se.type_contact,
                        2
                    )
                ) AS display_type_contact,
                se.type_contact,
                se.email_exact,
                se.id,
                se.photo,
                se.document_type,
                se.type_contact,
                se.type_client,
                se.first_name,
                se.last_name,
                se.agent_firstname,
                se.agent_lastname,
                se.ruc,
                se.document_number,

                cv.type_visit,
                cv.created_at,
                cv.longitude,
                cv.latitude
                FROM
                    api_sellercontact AS se
                LEFT JOIN api_client as cli ON
                se.client_id = cli.user_ptr_id
                INNER JOIN api_contactvisit AS cv ON
                se.id = cv.contact_id
                WHERE
                    se.type_contact IN (2, 1, 4)
                    and cv.created_at > "{}"
                    and cv.created_at < "{}"

                    and se.is_assigned = {}
                    and se.seller_id={}
                """.format(date_start, date_end, is_assigned, seller))

        serializer = SellerContactSerializer(contacts, many=True)

        return Response(serializer.data)

    def post(self, request):
        """Redefinido funcion para crear vendedor."""

        required = _("required")
        not_valid = _("not valid")
        data = request.data
        user_id = Operations.get_id(self, request)
        password = None
        send_email = False

        if user_id and request.user.role.id == 4:
            data['seller'] = user_id
        else:
            data['seller'] = None

        if 'type_contact' in data or ('password' not in data or (data['password'] is None or data['password'] is '')):
            # eliminamos contraseña para contacto en caso de envio
            if 'password' in data:
                del data["password"]

            # generamos contraseña random
            if 'type_contact' not in data or data['type_contact'] != 2:
                send_email = True
                password = ''.join(random.SystemRandom().choice(string.digits) for _ in range(6))
                data["password"] = password

        if data['seller'] is None:
            data['seller'] = Parameter.objects.get(parameter='platform_seller').value
            #TODO: Usar constantes. Eliminar numeros magicos
            data['latitude'] = '-12.1000244'
            data['longitude'] = '-76.9701127'
            data['type_contact'] = 1

        if "email_exact" not in data or not data["email_exact"]:
            raise serializers.ValidationError({'email_exact': [required]})

        # codigo de usuario se crea con su prefijo de especialista y su numero de documento
        if "type_client" not in data or not data["type_client"]:
            raise serializers.ValidationError({'type_client': [required]})

        if data["type_client"] == 'n':
            serializer = SellerContactNaturalSerializer(data=data)
        elif data["type_client"] == 'b':
            serializer = SellerContactBusinessSerializer(data=data)
        else:
            raise serializers.ValidationError({'type_client': [not_valid]})

        if serializer.is_valid():
            serializer.save()

            # Registrar nodos para contacto efectivo
            if 'test' not in sys.argv:
                if data['type_contact'] != 2:
                    # se le crea la lista de todas las categorias al cliente en firebase
                    pyrebase.createCategoriesLisClients(serializer.data['client_id'])

                    # envio de contraseña al cliente
                    if send_email:
                        mail = BasicEmailAmazon(subject='Envio Credenciales', to=data["email_exact"],
                                                template='email/send_credentials')
                        credentials = {}
                        credentials["user"] = data["email_exact"]
                        credentials["pass"] = password
                        mail.sendmail(args=credentials)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactObjectionsDetailView(APIView):
    """Detalle de Contacto."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsSeller)

    def get_object(self, pk):
        """Obtener Objeto."""
        visits = ContactVisit.objects.filter(contact=pk, type_visit=2).order_by('-created_at')
        if visits:
            return visits[0]
        else:
            raise Http404

    def get(self, request, pk):
        """Obtener Vendedor."""
        visit = self.get_object(pk)
        serializer = ContactVisitSerializer(visit)
        return Response(serializer.data)


class ContactFilterView(ListAPIView):
    """Listado de contactos."""
    # Listado de contactos pertenecientes al vendedor
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsSeller)
    serializer_class = SellerFilterContactSerializer

    def get_queryset(self):
        seller = Operations.get_id(self, self.request)
        contacts = SellerContact.objects.filter(seller=seller).exclude(type_contact=3).order_by('-created_at')

        # Filtro de tipo de contato (Mis contactos/Asignados)
        # assignment_type = 1 (Mis contactos)
        # assignment_type = 2 (Mis asignados)
        assignment_type = self.request.query_params.get('assignment_type', '1')
        if assignment_type is not None:
            if int(assignment_type) == 1:
                contacts = contacts.filter(is_assigned=False)
            elif int(assignment_type) == 2:
                contacts = contacts.filter(is_assigned=True)

        # Filetro de tipo de contacto
        # type_contact = 1 (Contactos efectivos. Tipo de contacto 1 que han subido un voucher)
        # type_contact = 2 (Contactos no efectivos. Tipo de contacto 2 + Tipo 1 que no hayan subido voucher)
        # type_contact = 4 (Contactos promocionales)
        type_contact = self.request.query_params.get('type_contact', None)
        if type_contact is not None:
            if int(type_contact) == 1:
                contacts = contacts.exclude(client__sale__file_url="").annotate(files_count=Count('client__sale__file_url')).filter(
                    type_contact=1, files_count__gt=0
                )
            elif int(type_contact) == 2:
                contacts = contacts.annotate(files_count=Count('client__sale__file_url')).filter(
                   Q (type_contact=2) | Q(
                        Q (files_count=0) | Q(client__sale__file_url=""),
                            type_contact=1

                    )
                )

                client__sale__file_url=""

            elif int(type_contact) == 4:
                contacts = contacts.filter(type_contact=4)

        # Filtro fecha desde y fecha hasta
        date_start = self.request.query_params.get('date_start', None)
        date_end = self.request.query_params.get('date_end', None)
        if date_start is not None and date_end is not None:
            fecha_end = datetime.strptime(date_end, '%Y-%m-%d')
            date_end = fecha_end + timedelta(days=1)
            contacts = contacts.filter(created_at__range=(date_start, date_end))
        return contacts


# ------------ Fin de Vendedores -----------------


# Subir la foto de un contacto
class PhotoContactUploadView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSeller)
    queryset = SellerContact.objects.all()
    parser_classes = (JSONParser, MultiPartParser)

    # localizo el usuario segun su id
    def get_object(self, pk):
        try:
            obj = SellerContact.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except SellerContact.DoesNotExist:
            raise Http404

    # metodo para actualizar
    def put(self, request, pk):
        data = request.data
        contact = self.get_object(pk)
        media_serializer = MediaSerializer(
            data=data,
            partial=True
        )
        # creando nombre de archivo
        filename = str(uuid.uuid4())
        filename = filename + '.png'
        if media_serializer.is_valid():
            destination = open(filename, 'wb+')
            for chunk in data['photo'].chunks():
                destination.write(chunk)
            destination.close()
        else:
            raise serializers.ValidationError(media_serializer.errors)
        # se sube el archivo a amazon
        name_photo = upload_photo_s3(filename)
        os.remove(filename)  # se elimina del server local
        serializer = ContactPhotoSerializer(contact, data={'photo': name_photo},
                                            partial=True)

        try:
            user = User.objects.get(username=contact.email_exact)
            serializer_user = UserPhotoSerializer(user,
                                                  data={'photo': name_photo},
                                                  partial=True)
        except User.DoesNotExist:
            serializer_user = None

        if serializer.is_valid():
            serializer.save()

            if serializer_user and serializer_user.is_valid():
                serializer_user.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Subir la foto de un usuario
class PhotoUploadView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    parser_classes = (JSONParser, MultiPartParser)

    # localizo el usuario segun su id
    def get_object(self, pk):
        try:
            obj = User.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except User.DoesNotExist:
            raise Http404

    # metodo para actualizar
    def put(self, request, pk):
        data = request.data
        user = self.get_object(pk)
        media_serializer = MediaSerializer(
            data=data,
            partial=True
        )
        # creando nombre de archivo
        filename = str(uuid.uuid4())
        filename = filename + '.png'
        if media_serializer.is_valid():
            destination = open(filename, 'wb+')
            for chunk in data['photo'].chunks():
                destination.write(chunk)
            destination.close()
        else:
            raise serializers.ValidationError(media_serializer.errors)
        # se sube el archivo a amazon
        name_photo = self.upload_photo_s3(filename)
        os.remove(filename)  # se elimina del server local
        serializer = UserPhotoSerializer(user,
                                         data={'photo': name_photo},
                                         partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # metodo para subir foto a s3
    def upload_photo_s3(self, filename):

        # subir archivo con libreria boto
        s3 = boto3.client('s3')

        s3.upload_file(
            filename, 'linkup-photos', filename,
            ExtraArgs={'ACL': 'public-read'}
        )
        # devolviendo ruta al archivo
        return 'https://s3.amazonaws.com/linkup-photos/' + filename;


# --------------------------------------------------

class FileUploadView(ListCreateAPIView, UpdateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Specialist.objects.all()
    serializer_class = MediaSerializer
    parser_classes = (JSONParser, MultiPartParser)

    def post(self, request):
        data = request.data

        serializer = MediaSerializer(
            data=data,
            partial=True
        )

        # creando nombre de archivo
        filename = str(uuid.uuid4())
        filename = filename + '.png';

        if serializer.is_valid():
            # serializer.save()

            destination = open(filename, 'wb+')
            for chunk in data['photo'].chunks():
                destination.write(chunk)

            destination.close()

        name = self.uploadImageToS3(filename)

        # eliminar archivo temporal

        # guardar archivo en disco
        # reemplazar por subir imagen al aws
        return Response(serializer.data['filename'] + str(name))

    def uploadImageToS3(self, filename):

        # subir archivo con libreria boto
        s3 = boto3.client('s3')

        s3.upload_file(
            filename, 'linkup-photos', filename,
            ExtraArgs={'ACL': 'public-read'}
        )

        # devolviendo ruta al archivo
        return 'https://s3.amazonaws.com/linkup-photos/' + filename;


class AllFileUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, filename, format=None):
        file_obj = request.data['file']

        destination = open('/Users/alfonsomunoz/' + filename, 'wb+')
        for chunk in file_obj.chunks():
            destination.write(chunk)

        destination.close()

        return Response(status=204)


class DocumentUploadView(APIView):
    """
        Actualizacion de imagen referente al documento de identidad
    """
    permission_classes = (IsAdminOrOwner,)
    queryset = User.objects.all()
    parser_classes = (JSONParser, MultiPartParser)

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        data = request.data
        user = self.get_object(pk)
        media_serializer = MediaSerializer(
            data=data,
            partial=True
        )
        # creando nombre de archivo
        filename = str(uuid.uuid4())
        filename = filename + '.png';
        if media_serializer.is_valid():
            destination = open(filename, 'wb+')
            for chunk in data['img_document_number'].chunks():
                destination.write(chunk)
            destination.close()
        else:
            raise serializers.ValidationError(media_serializer.errors)

        # pdb.set_trace()
        name_photo = upload_photo_s3(filename)
        os.remove(filename)
        serializer = UserSerializer(user, data={'img_document_number': name_photo}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def upload_photo_s3(filename):
    # subir archivo con libreria boto
    s3 = boto3.client('s3')

    s3.upload_file(
        filename, 'linkup-photos', filename,
        ExtraArgs={'ACL': 'public-read'}
    )
    # devolviendo ruta al archivo
    return 'https://s3.amazonaws.com/linkup-photos/' + filename;

class RucDetailView(APIView):
    """
        Traer informacion de RUC
    """
    permission_classes = (IsAdminOrOwner,)
    queryset = User.objects.all()
    parser_classes = (JSONParser, MultiPartParser)

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        import requests
        from api.serializers.actors import RucApiDetailSerializer
        from linkupapi import settings_secret

        url = "https://ruc.com.pe/api/v1/ruc"
        payload = {
          "token": settings_secret.TOKEN_RUC,
          "ruc": pk
        }

        try:
            response = requests.post(url, json=payload, timeout=2.5)
        except Exception as e:
            response = None

        try:
            url_sunat = "https://api.sunat.cloud/ruc/{ruc}".format(ruc=pk)
            response2 = requests.get(url_sunat, timeout=2.5)
        except Exception as e:
            response2 = response

        # Se evaluan las 2 respuestas
        if response and response.status_code == 200 and response2.status_code == 200:
            data = {'ruc': str(pk)}
            # Convinamos los diccionarios
            data = dict(data, **response.json())

            data['cellphone'] = data['telephone'] = data['code_cellphone'] = data['code_telephone'] = ""
            if 'telefono' in response2.json():
                telefonos = response2.json()['telefono']
                phones = telefonos.split('|')
                for phone in phones:
                    if phone[0]=='9':
                        data['cellphone'] = phone
                    else:
                        data['telephone'] = phone

            if 'nombre_comercial' in response2.json():
                data['commercial_reason'] = response2.json()['nombre_comercial']
            else:
                data['commercial_reason'] = ""

            serializer = RucApiDetailSerializer(data, partial=True)
            return Response(serializer.data)
        raise Http404

class SupportActorsView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    required = _("required")
    def post(self, request):
        data = request.data
        subject = ''

        if 'query' in request.data:
            pass
        else:
            raise serializers.ValidationError({'query': [self.required]})

        if 'message' in request.data:
            pass
        else:
            raise serializers.ValidationError({'message': [self.required]})

        if request.user.role.id == ROLE_CLIENT:
            subject = 'Atención al Cliente'
        elif request.user.role.id == ROLE_SPECIALIST:
            subject = 'Soporte - Especialista'
        elif request.user.role.id == ROLE_SELLER:
            subject = 'Soporte - Vendedor'

        if 'test' not in sys.argv:

            name = "{} {}".format(request.user.first_name, request.user.last_name)
            phone = "{} | {}".format(request.user.cellphone, request.user.photo)

            data_email = {
                        'title':subject,
                        'name': name,
                        'email':request.user.email_exact,
                        'phone':phone,
                        'query': data['query'],
                        'message': data['message'],
                    }

            try:
                parameter = Parameter.objects.get(parameter="support")
            except Parameter.DoesNotExist:
                logger.error("support no existe en tabla parametros")
                raise Http404

            mail = BasicEmailAmazon(subject=subject,
                to=parameter.value, template='email/support')

            response = mail.sendmail(args=data_email)


        return Response({})
