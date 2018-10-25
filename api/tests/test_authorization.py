"""Pruebas para autorizaciones."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from rest_framework import status
from ..models import Client as Cliente

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')


class ChangeStatusClient(APITestCase):
    """Se puede cambiar el status del cliente."""

    fixtures = ['data', 'data2', 'data3']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            'username': 'darwin',
            'password': 'intel12345',
            'nick': 'dar',
            'type_client': 'n',
            'first_name': 'darwin',
            'last_name': 'vasquez',
            'civil_state': 's',
            'birthdate': '1998-09-19',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'sex': 'm',
            'document_type': 3,
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'activity_description': 'Loremp iptsum',
            'level_instruction': 1,
            'institute': 'UNEFA',
            'profession': "Administrador",
            'ocupation': 1,
            'about': 'iptsum aabout',
            'ciiu': 1,
            'nationality': 1,
            'residence_country': 1
        }

    def test_change_to_active(self):
        """Cambia el status del cliente a Activo."""
        data = {"status": 1}
        send = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        
        response = client.put(reverse('auth-clients',
                              kwargs={'pk': send.data['client_id']}),
                              data, format='json')

        c = Cliente.objects.get(pk=send.data['client_id'])
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["status"], int(c.status))

    def test_change_to_pending(self):
        """Cambia el status del cliente a Pending."""
        data = {"status": 1}
        send = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = client.put(reverse('auth-clients',
                              kwargs={'pk': send.data['client_id']}),
                              data, format='json')

        c = Cliente.objects.get(pk=send.data['client_id'])
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["status"], int(c.status))

    def test_change_to_rejected(self):
        """Cambia el status del cliente a Rechazado."""
        data = {"status": 2}
        send = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = client.put(reverse('auth-clients',
                              kwargs={'pk': send.data['client_id']}),
                              data, format='json')

        c = Cliente.objects.get(pk=send.data['client_id'])
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["status"], int(c.status))

    def test_invalid_status(self):
        """Envio de Status invalido."""
        data = {"status": 10}
        send = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = client.put(reverse('auth-clients',
                              kwargs={'pk': send.data['client_id']}),
                              data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetClientsToAuthorization(APITestCase):
    """Test creado para probar los listados y autorizaciones de procesos"""
    fixtures = ['data','data2','data3','test_authorization']
    def setUp(self):
        self.valid_payload = {
            'name': 'julia',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            "type_specialist": "m",
            'photo': 'preview.jpg',
            'document_type': 3,
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            "ruc": "2009918312",
            "business_name": "agropatria",
            "payment_per_answer": 2.2,
            "category": 1
        }

    def test_get_all_clients(self):
        """Trae listado de clientes ordenados por estatus de autorizacion y compara con el primer registro traido"""
        result_expected = {
            "code_seller": None,
            "name":"Don Venus",
            "document":"34354367",
            "document_type":"RUC",
            "status":1,
            "document_type_name":"RUC",
            "date_join": "2017-11-13",
            "id": 4
        }

        # get API response
        response = client.get(reverse('auth-list-clients'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0], result_expected)
