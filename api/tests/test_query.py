"""Pruebas unitarias para las consultas."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Client as Cliente
from rest_framework import status
from api.serializers.actors import ClientSerializer
# Create your tests here.

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')  # Api Admin


class GetListQueries(APITestCase):
    """Prueba devolver especialidades por consulta hecha del cliente."""

    fixtures = ['data', 'data2', 'data3', 'test_query']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer HhaMCycvJ5SCLXSpEo7KerIXcNgBSt')

    def test_get_list_by_client_wrong_role(self):
        """Permiso no autorizado."""
        client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = client.get(reverse('queries-client'))
        # import pdb; pdb.set_trace()
        # clients = Cliente.objects.all()
        # serializer = ClientSerializer(clients, many=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_list_by_client(self):
        """Devolver categorias ordenadas por ultimo msj."""
        response = self.client.get(reverse('queries-client'))
        self.assertEqual(response.data[0]['status_message'], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
