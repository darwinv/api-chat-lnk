
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from api.models import User, Client, Category, Specialist, Seller
from api.serializers.actors import ClientSerializer, UserPhotoSerializer
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from django_filters import rest_framework as filters
from rest_framework import filters as searchfilters
# import django_filters.rest_framework
from api.serializers.actors import UserSerializer, SpecialistSerializer
from api.serializers.actors import SpecialistAccountSerializer, SellerSerializer, MediaSerializer
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

class ClientListView(ListCreateAPIView, UpdateAPIView):
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

    def post(self, request):
        data = request.data
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

class ClientDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_object(self, pk):
        try:
            return Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        client = self.get_object(pk)
        serializer = ClientSerializer(client)
        return Response(serializer.data)

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

class SpecialistListView(ListCreateAPIView, UpdateAPIView):
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
        # pdb.set_trace()
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


    def post(self, request):
        data = request.data
        data['code'] = PREFIX_CODE_SPECIALIST + request.data.get('document_number')
        data['role'] = ROLE_SPECIALIST
        serializer = SpecialistSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        print("------------------------------------")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SpecialistDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    def get_object(self, pk):
        try:
            return Specialist.objects.get(pk=pk)
        except Specialist.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        specialist = self.get_object(pk)
        serializer = SpecialistSerializer(specialist)
        return Response(serializer.data)

    def put(self, request, pk):
        data = request.data
        specialist = self.get_object(pk)
        data['code'] = PREFIX_CODE_SPECIALIST + request.data.get('document_number',specialist.document_number)
        data['photo'] = request.data.get('photo',specialist.photo)
        data['username'] = specialist.username
        data['role'] = ROLE_SPECIALIST

        serializer = SpecialistSerializer(specialist, data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        specialist = self.get_object(pk)
        specialist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

class SellerListView(ListCreateAPIView, UpdateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

    # funcion para localizar especialista principal
    def get_object(self, pk):
        try:
            return Seller.objects.get(pk=pk,type_specialist='m')
        except Seller.DoesNotExist:
            raise Http404

    # Funcion personalizada para
    # devolver los especialistas asociados a un principal si envian el
    #  parametro [main_specialist]
    def list(self, request):

        queryset = self.get_queryset()
        serializer = SellerSerializer(queryset, many=True)

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

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

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

        name_photo = self.upload_photo_s3(filename)
        os.remove(filename)
        serializer = UserPhotoSerializer(user, data={'photo': name_photo }, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
