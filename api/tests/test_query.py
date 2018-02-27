"""Pruebas unitarias para las consultas."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
import json
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
        """Primer mensaje retornado es Viewed False y estatus 200."""
        parameters = {'category': 8}
        response = self.client.get(reverse('query-chat-client'), parameters)

        self.assertEqual(response.data['results'][0]['message']['viewed'], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateQuery(APITestCase):
    """Prueba para crear consulta."""

    fixtures = ['data', 'data2', 'data3', 'test_query']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer HhaMCycvJ5SCLXSpEo7KerIXcNgBSt')
        self.valid_payload = {
            "title": "Pago de Impuestos",
            "category": 24,
            "message": {
                "message": "Lorem ipsum dolor sit amet,anctus e",
                "msg_type": "q",
                "media_files": []
            }
        }

    def test_create_query(self):
        """Creacion Exitosa de la consulta."""
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
