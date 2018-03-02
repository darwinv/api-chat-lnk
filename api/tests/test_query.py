"""Pruebas unitarias para las consultas."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from api.models import SpecialistMessageList
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

    def test_get_list_by_client_whitout_id(self):
        """404 clien_id not found."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = client.get(reverse('queries-client'))
        
        # import pdb; pdb.set_trace()
        # clients = Cliente.objects.all()
        # serializer = ClientSerializer(clients, many=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_list_by_client(self):
        """Devolver categorias ordenadas por ultimo msj."""
        response = self.client.get(reverse('queries-client'))
        self.assertEqual(response.data[0]['status_message'], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetChatClientListQueries(APITestCase):
    """Prueba devolver especialidades por consulta hecha del cliente."""

    fixtures = ['data', 'data2', 'data3', 'test_chat']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer kEphPGlavEforKavpDzuZSgK0zpoXS')

    def test_get_list_by_client_chat(self):
        """primer mensaje retornado es Viewed False y estatus 200"""
        parameters = {'category': 8}
        response = self.client.get(reverse('query-chat-client'), parameters)
        
        self.assertEqual(response.data['results'][0]['message']['viewed'], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_by_client_chat_from_admin(self):
        """Admin prueba si primer mensaje user 15 no ha sido visto"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        parameters = {'category': 8, 'client_id': 15}
        response = self.client.get(reverse('query-chat-client'), parameters)
        
        self.assertEqual(response.data['results'][0]['message']['viewed'], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_bad_client_chat_from_admin(self):
        """Admin trae mensaje de user 14 (404)"""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        parameters = {'category': 8, 'client_id': 14}
        response = self.client.get(reverse('query-chat-client'), parameters)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetSpecialistMessages(APITestCase):
    """Prueba para devolver el plan activo y elegido de un determinado cliente"""

    fixtures = ['data', 'data2', 'data3', 'test_getspecialistmessages']

    def setUp(self):
        """Setup."""
        pass

    def test_get_list_messages_token_specialist(self):
        """Obtener resultado 200."""
        #se provee un token de especialista el cuel tiene   mensajes pendientes de responders
        self.client.credentials(HTTP_AUTHORIZATION='Bearer rRNQmSvkyHvi80qkYplRvLmckV3DYy')
        response = self.client.get(reverse('specialists-list-messages'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)