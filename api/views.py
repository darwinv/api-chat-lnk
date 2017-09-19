from django.shortcuts import render
from rest_framework.views import APIView
from api.models import User, Client
from api.serializers import ClientSerializer
from rest_framework.response import Response
# Create your views here.

class ClientView(APIView):
    # Lista todos los clientes naturales o crea uno nuevo
    # no olvidar lo de los permisos permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = {
            'name': request.data.get('name'),
            'age': int(request.data.get('age')),
            'breed': request.data.get('breed'),
            'color': request.data.get('color')
        }
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def perform_create(self, serializer):
    #     serializer.save()
