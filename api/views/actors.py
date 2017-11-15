
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from api.models import User, Client, Specialist, Seller, Product, Purchase

from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework import serializers
from django.db.models import Sum
from django_filters import rest_framework as filters
from rest_framework import filters as searchfilters
from api.serializers.actors import ClientSerializer, UserPhotoSerializer
from api.serializers.actors import UserSerializer, SpecialistSerializer
from api.serializers.actors import SellerSerializer, SellerAccountSerializer, MediaSerializer
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.parsers import JSONParser, MultiPartParser, FileUploadParser
import pdb, os
import uuid
import boto3

# Create your views here.

# Constantes
PREFIX_CODE_CLIENT = 'c'
ROLE_CLIENT = 2
ROLE_SPECIALIST = 3
PREFIX_CODE_SPECIALIST = 's'
DATE_FAKE = '1900-01-01'
# Fin de constates


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('username',)

# Vista para Listar y Crear Clientes
class ClientListView(ListCreateAPIView):
    # Lista todos los clientes naturales o crea uno nuevo
    # no olvidar lo de los permisos permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    permission_classes = [permissions.AllowAny]
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    filter_backends = (filters.DjangoFilterBackend,searchfilters.SearchFilter,)
    filter_fields = ('nick',)
    search_fields = ('email_exact', 'first_name')

    # def get(self, request):
    #    clients = Client.objects.all()
    #    serializer = ClientSerializer(clients, many=True)
    #    return Response(serializer.data)

    # Metodo post redefinido
    def post(self, request):
        data = request.data
        # codigo de usuario se crea con su prefijo de cliente y su numero de documento
        data['code'] = PREFIX_CODE_CLIENT + str(request.data.get('document_number'))
        data['role'] = ROLE_CLIENT
        if data['type_client'] == 'n':
            data['economic_sector'] = ''
            data['commercial_group'] = ''
        elif data['type_client'] == 'b':
            data['birthdate'] = DATE_FAKE
            data['sex'] = ''
            data['civil_state'] = ''
            data['level_instruction'] = ''
            data['profession'] = ''
            data['ocupation'] = ''

        serializer = ClientSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

# Vista para Detalle del Cliente

class ClientDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Metodo para devolver objeto
    def get_object(self, pk):
        try:
            return Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        client = self.get_object(pk)
        serializer = ClientSerializer(client)
        return Response(serializer.data)


# Vista para detalle del cliente segun su username
# se hizo con la finalidad de instanciar una vez logueado
class ClientDetailByUsername(APIView):
    def get_object(self, username):
        try:
            return Client.objects.get(username=username)
        except Client.DoesNotExist:
            raise Http404

    def get(self, request, username):
        client = self.get_object(username)
        serializer = ClientSerializer(client)
        return Response(serializer.data)


# Fin de Clientes

#---------- ------ Inicio de Especialistas ------------------------------
# Vista para Listado y Creacion de Especialista
class SpecialistListView(ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer

    # funcion para localizar especialista principal
    def get_object(self, pk):
        try:
            return Specialist.objects.get(pk=pk,type_specialist='m')
        except Specialist.DoesNotExist:
            raise Http404

    # Funcion personalizada para
    # devolver los especialistas asociados a un principal si envian el
    #  parametro [main_specialist]
    def list(self, request):

        # en dado caso que exista el parametro "main_specialist", se devuelve
        # el listado de especialistas asociados, caso contrario devuelve todos
        if 'main_specialist' in request.query_params:
            specialist = self.get_object(request.query_params["main_specialist"])
            queryset = Specialist.objects.filter(category_id=specialist.category).exclude(type_specialist='m')
            serializer = SpecialistSerializer(queryset, many=True)
        else:
            queryset = self.get_queryset()
            serializer = SpecialistSerializer(queryset, many=True)

        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    # Funcion para crear un especialista
    def post(self, request):
        data = request.data
        # codigo de usuario se crea con su prefijo de especialista y su numero de documento
        data['code'] = PREFIX_CODE_SPECIALIST + request.data.get('document_number')
        data['role'] = ROLE_SPECIALIST
        serializer = SpecialistSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para el detalle del especialista, actualizacion y borrado
class SpecialistDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    # metodo para devolver la instancia segun id
    def get_object(self, pk):
        try:
            return Specialist.objects.get(pk=pk)
        except Specialist.DoesNotExist:
            raise Http404
    # detalle
    def get(self, request, pk):
        specialist = self.get_object(pk)
        serializer = SpecialistSerializer(specialist)
        return Response(serializer.data)
    # actualizacion
    def put(self, request, pk):
        data = request.data
        specialist = self.get_object(pk)
        # codigo de usuario se crea con su prefijo de especialista y su numero de documento
        data['code'] = PREFIX_CODE_SPECIALIST + request.data.get('document_number',specialist.document_number)
        data['photo'] = request.data.get('photo',specialist.photo)
        data['username'] = specialist.username
        data['role'] = ROLE_SPECIALIST

        serializer = SpecialistSerializer(specialist, data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # borrado
    def delete(self,request,pk):
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


#---------- ------ Inicio de Vendedores ------------------------------

class SellerFilter(filters.FilterSet):
    count_plans_seller = filters.NumberFilter(name='count_plans_seller', method='filter_count_plans')
    count_queries_seller = filters.NumberFilter(name='count_queries_seller', method='filter_count_queries')

    def filter_count_plans(self, qs, name, value):
        #todos los id de vendedores que han vendido mas que value
        sellers_ids = []
        for seller in Seller.objects.all():
            #calcular cantidad vendida
            count = Purchase.objects.filter(seller=seller.id).count()

            #si la cantidad vendida es mayor que el parametro
            #agregar a la lista
            if count > value:
                sellers_ids.append(seller.id)
        return qs.filter(id__in= sellers_ids)

    def filter_count_queries(self, qs, name, value):
        #todos los id de vendedores que han vendido mas que value
        sellers_ids = []
        for seller in Seller.objects.all():
            #calcular cantidad vendida
            count_result = Product.objects.filter(purchase__seller__isnull=False, purchase__seller=seller.id).aggregate(Sum('query_amount'))
            count = count_result['query_amount__sum']
            #si la cantidad vendida es mayor que el parametro
            #agregar a la lista
            if count and count > value:
                sellers_ids.append(seller.id)
        return qs.filter(id__in= sellers_ids)

    first_name = filters.CharFilter(name='first_name', lookup_expr='icontains')
    last_name = filters.CharFilter(name='last_name', lookup_expr='icontains')
    ruc = filters.CharFilter(name='ruc', lookup_expr='icontains')
    email_exact = filters.CharFilter(name='email_exact', lookup_expr='icontains')

    class Meta:
        model = Seller
        fields = ['first_name', 'last_name', 'ruc', 'email_exact']

class SellerListView(ListCreateAPIView, UpdateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = SellerFilter


class SellerDetailView(APIView):
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

class SellerAccountView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = SellerAccountSerializer

    def get_object(self, pk):
        try:
            return Specialist.objects.get(pk=pk)
        except Specialist.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        # creacion de QuerySet para listadaos
        queryset = Seller.objects.filter(id=pk,purchase__fee__status=1)\
            .values('id','purchase__total_amount',
                                  'purchase__id','purchase__code','purchase__query_amount','purchase__fee_number',
                                  'purchase__product__is_billable','purchase__product__expiration_number','purchase__product__name',
                                  'purchase__client__code','purchase__client__nick', 'purchase__fee__date', 'purchase__fee__id',
                                  'purchase__fee__fee_amount','purchase__fee__status','purchase__fee__payment_type__name',
                                  'purchase__fee__reference_number','purchase__fee__fee_order_number',
                                  )\
            .order_by('purchase__fee__date')

        print(queryset.query)
        print("------------------------------------")
        serializer = SellerAccountSerializer(queryset, many=True)
        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


# ------------ Fin de Vendedores -----------------

# Subir la foto de un usuario
class PhotoUploadView(APIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    parser_classes = (JSONParser, MultiPartParser)

    # localizo el usuario segun su id
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    # metodo para actualizar
    def put(self, request, pk):
        data = request.data
        user = self.get_object(pk)
        media_serializer = MediaSerializer(
            data = data,
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
        os.remove(filename) # se elimina del server local
        serializer = UserPhotoSerializer(user, data={'photo': name_photo }, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # metodo para subir foto a s3
    def upload_photo_s3(self, filename):

        #subir archivo con libreria boto
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
            data = data,
            partial=True
        )

        # creando nombre de archivo
        filename = str(uuid.uuid4())
        filename = filename + '.png';

        if serializer.is_valid():
            #serializer.save()

            destination = open(filename, 'wb+')
            for chunk in data['photo'].chunks():
                destination.write(chunk)

            destination.close()

        name=self.uploadImageToS3(filename)

        #eliminar archivo temporal

        #guardar archivo en disco
        #reemplazar por subir imagen al aws
        return Response(serializer.data['filename']+str(name))

    def uploadImageToS3(self, filename):

        #subir archivo con libreria boto
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
