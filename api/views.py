
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from api.models import User, Client, Category, Specialist
from api.serializers import ClientSerializer
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
import django_filters.rest_framework
from api.serializers import UserSerializer, CategorySerializer, SpecialistSerializer
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
# Create your views here.

# Constantes
PREFIX_CODE_CLIENT = 'c'
ROLE_CLIENT = 2
ROLE_SPECIALIST = 3
PREFIX_CODE_SPECIALIST = 's'
DATE_FAKE = '1900-01-01'
#Fin de constates


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('username',)

class ClientListView(ListCreateAPIView, UpdateAPIView):
    # Lista todos los clientes naturales o crea uno nuevo
    # no olvidar lo de los permisos permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    permission_classes = [permissions.AllowAny]
    serializer_class = ClientSerializer
    queryset = Client.objects.all()

    #def get(self, request):
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

# Fin de Clientes

class CategoryListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get(self, request):
        specialities = Category.objects.all()
        serializer = CategorySerializer(specialities, many=True)
        return Response(serializer.data)

class CategoryDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
# ------------ Fin de Categorias o Especialidades -----------------

#---------- ------ Inicio de Especialistas ------------------------------

class SpecialistListView(ListCreateAPIView, UpdateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer

    #def get(self, request):
    #   specialists = Specialist.objects.all()
    #   serializer = SpecialistSerializer(specialists, many=True)
    #   return Response(serializer.data)

    def post(self, request):
        data = request.data
        data['code'] = PREFIX_CODE_SPECIALIST + request.data.get('document_number')
        data['role'] = ROLE_SPECIALIST
        serializer = SpecialistSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
