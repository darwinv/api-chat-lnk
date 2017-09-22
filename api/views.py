
from rest_framework.views import APIView
from api.models import Client
from api.serializers import ClientSerializer
from rest_framework.response import Response
from rest_framework import status, permissions

# Create your views here.

# Constantes
PREFIX_CODE_CLIENT = 'c'
ROLE_CLIENT = 2
#Fin de constates

class ClientView(APIView):
    # Lista todos los clientes naturales o crea uno nuevo
    # no olvidar lo de los permisos permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        data['code'] = PREFIX_CODE_CLIENT + request.data.get('document_number')
        data['role'] = ROLE_CLIENT
        if data['type_client'] == 'n':
            data['economic_sector'] = ''
            data['commercial_group'] = ''
        serializer = ClientSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    # def perform_create(self, serializer):
    #     serializer.save()
