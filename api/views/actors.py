"""Vista de todos los Actores."""
# from api.logger import manager
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from api.models import User, Client, Specialist, Seller, Query
from api.models import SellerContactNoEfective, SpecialistMessageList, SpecialistMessageList_sp
from api.models import RecoveryPassword
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, generics
from rest_framework import serializers
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasReadWriteScope, TokenHasScope
from django.db.models import Sum, Manager
from django_filters import rest_framework as filters
from rest_framework import filters as searchfilters
from api.serializers.actors import ClientSerializer, UserPhotoSerializer, KeySerializer
from api.serializers.actors import UserSerializer, SpecialistSerializer, SellerContactNaturalSerializer
from api.serializers.actors import SellerSerializer, SellerContactBusinessSerializer
from api.serializers.actors import MediaSerializer, ChangePasswordSerializer, SpecialistMessageListCustomSerializer
from api.serializers.query import QuerySerializer, QueryCustomSerializer
from django.http import Http404
from api.permissions import IsAdminOnList, IsAdminOrOwner, IsSeller, IsAdminOrSpecialist
from rest_framework.parsers import JSONParser, MultiPartParser, FileUploadParser
from django.utils.translation import ugettext_lazy as _
import os
import uuid
import boto3
from datetime import datetime, date
from django.utils import timezone
from api.utils.validations import Operations
from api import pyrebase
from api.emails import BasicEmailAmazon


# Constantes
PREFIX_CODE_CLIENT = 'C'
ROLE_CLIENT = 2
ROLE_SPECIALIST = 3
ROLE_SELLER = 4
PREFIX_CODE_SPECIALIST = 'E'
PREFIX_CODE_SELLER = 'V'
DATE_FAKE = '1900-01-01'
# Fin de constantes

#obtener el logger con la configuracion para actors
# loggerActor = manager.setup_log(__name__)

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
        data = {'code':code}
        mail = BasicEmailAmazon(subject="Codigo de cambio de contraseña", to=email, template='send_code')
        return Response(mail.sendmail(args=data))

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
        # import pdb
        # pdb.set_trace()
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


from api.models import QueryPlansAcquired, SaleDetail, Sale
from api.models import Clasification, QueryPlans, ProductType
from datetime import datetime
from api.utils import tools
from api.pyrebase import chosen_plan
from api.serializers.plan import QueryPlansAcquiredSerializer

def give_plan_new_client(client_id):
    """OJO."""
    """FUNCION CREADA PARA OTORGAR PLANES A CLIENTES NUEVOS"""
    """ESTA FUNCION DEBE SER BORRADA DESPUES DE TENER EL MODULO DE COMPRAS"""
    sale = Sale()
    saleDetail = SaleDetail()
    queryPlansAcquired = QueryPlansAcquired()

    try:
        product_type = ProductType.objects.get(pk=1)
    except Exception as e:
        product_type = ProductType()
        product_type.name = 'TesterType'
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
        query_plans = QueryPlans.objects.get(pk=1)
    except Exception as e:
        query_plans = QueryPlans()
        query_plans.product_type = product_type
        query_plans.clasification = clasification
        query_plans.id = '1'
        query_plans.query_quantity = '0'
        query_plans.validity_months = '0'
        query_plans.maximum_response_time = '0'
        query_plans.is_active = '0'
        query_plans.price = '0.0000'
        query_plans.save()

    sale.created_at = datetime.now()
    sale.place = 'BCP'
    sale.total_amount = '1000.00'
    sale.reference_number = 'CD1004'
    sale.description = 'Test Venta'
    sale.is_fee = '1'
    sale.client_id = client_id
    sale.save()

    saleDetail.price = '1000.00'
    saleDetail.description = 'Plan de Prueba'
    saleDetail.discount = '0.00'
    saleDetail.pin_code = tools.ramdon_generator(6)
    saleDetail.is_billable = '0'
    saleDetail.contract_id = None
    saleDetail.product_type_id = '1'
    saleDetail.sale_id = sale.id
    saleDetail.save()

    queryPlansAcquired.expiration_date = '2019-04-09'
    queryPlansAcquired.validity_months = '6'
    queryPlansAcquired.available_queries = '500'
    queryPlansAcquired.activation_date = None
    queryPlansAcquired.is_active = '1'
    queryPlansAcquired.available_requeries = '1'
    queryPlansAcquired.maximum_response_time = '24'
    queryPlansAcquired.acquired_at = datetime.now()
    queryPlansAcquired.client_id = client_id
    queryPlansAcquired.query_plans_id = '1'
    queryPlansAcquired.sale_detail_id = saleDetail.id
    queryPlansAcquired.query_quantity = '500'
    queryPlansAcquired.plan_name = 'TesterPack'
    queryPlansAcquired.is_chosen = '1'
    queryPlansAcquired.save()

    serializer = QueryPlansAcquiredSerializer(queryPlansAcquired)
    chosen_plan('u'+str(client_id), serializer.data)

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

    # def get(self, request):
    #    clients = Client.objects.all()
    #    serializer = ClientSerializer(clients, many=True)
    #    return Response(serializer.data)

    # Metodo post redefinido
    def post(self, request):
        """Redefinido metodo para crear clientes."""
        data = request.data
        if 'type_client' not in data or not data['type_client']:
            raise serializers.ValidationError({'type_client': [self.required]})
        if data['type_client'] == 'n':
            data['economic_sector'] = ''
        elif data['type_client'] == 'b':
            data['birthdate'] = DATE_FAKE
            data['sex'] = ''
            data['civil_state'] = ''
            data['level_instruction'] = ''
            data['profession'] = ''
            data['ocupation'] = ''
        data['role'] = ROLE_CLIENT
        serializer = ClientSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # se le crea la lista de todas las categorias al cliente en firebase
            pyrebase.createCategoriesLisClients(serializer.data['id'])


            # FUNCION TEMPORAL PARA OTORGAR PLANES A CLIENTES
            give_plan_new_client(serializer.data['id']) # OJO FUNCION TEMPORAL
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

# Vista para Detalle del Cliente
class ClientDetailView(APIView):
    """Detalle del Cliente, GET/PUT/Delete."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAdminOrOwner,)

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
        serializer = ClientSerializer(client)
        return Response(serializer.data)

        data['username'] = specialist.username
        data['role'] = ROLE_SPECIALIST

        serializer = SpecialistSerializer(specialist, data, partial=True,
                                          context={'request': request})
        
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
        data['code'] = PREFIX_CODE_SPECIALIST + request.data.get('document_number')
        data['role'] = ROLE_SPECIALIST
        serializer = SpecialistSerializer(
            data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = (IsAdminOrOwner,)

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
        data['code'] = PREFIX_CODE_SPECIALIST + request.data.get(
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


# Vista para estado de cuenta de especialista
class SpecialistAccountView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Specialist.objects.get(pk=pk)
        except Specialist.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        specialist = self.get_object(pk)
        serializer = SpecialistAccountSerializer(specialist)
        return Response(serializer.data)


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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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


class SellerDetailByUsername2(APIView):
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


class SellerAccountView(ListCreateAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAdminUser,)

    def get_object(self, pk):
        try:
            return Specialist.objects.get(pk=pk)
        except Specialist.DoesNotExist:
            raise Http404

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


class ContactListView(ListCreateAPIView):
    """Vista para Contacto No Efectivo."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsSeller,)
    # aca se debe colocar el serializer para listar todos
    serializer_class = SellerContactNaturalSerializer
    queryset = SellerContactNoEfective.objects.all()

    def post(self, request):
        """Redefinido funcion para crear vendedor."""
        required = _("required")
        not_valid = _("not valid")
        data = request.data
        # codigo de usuario se crea con su prefijo de especialista y su numero de documento
        if "type_contact" not in data or not data["type_contact"]:
            raise serializers.ValidationError({'type_contact': [required]})

        if data["type_contact"] == 'n':
            serializer = SellerContactNaturalSerializer(data=data)
        elif data["type_contact"] == 'b':
            serializer = SellerContactBusinessSerializer(data=data)
        else:
            raise serializers.ValidationError({'type_contact': [not_valid]})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------ Fin de Vendedores -----------------

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
        filename = filename + '.png';
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
