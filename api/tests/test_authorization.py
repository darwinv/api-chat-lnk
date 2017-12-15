"""Pruebas para autorizaciones."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from rest_framework import status
from ..models import Client as Cliente

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')


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
            'birthdate': '2017-09-19',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'sex': 'm',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'activity_description': 'Loremp iptsum',
            'level_instruction': 1,
            'institute': 'UNEFA',
            'profession': "Administrador",
            'ocupation': '0',
            'about': 'iptsum aabout',
            'ciiu': '1440',
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
        client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = client.put(reverse('auth-clients',
                              kwargs={'pk': send.data["id"]}),
                              data, format='json')

        c = Cliente.objects.get(pk=send.data["id"])
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["status"], int(c.status))

    def test_change_to_pending(self):
        """Cambia el status del cliente a Pending."""
        data = {"status": 0}
        send = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = client.put(reverse('auth-clients',
                              kwargs={'pk': send.data["id"]}),
                              data, format='json')

        c = Cliente.objects.get(pk=send.data["id"])
        # import pdb; pdb.set_trace()
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
        client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = client.put(reverse('auth-clients',
                              kwargs={'pk': send.data["id"]}),
                              data, format='json')

        c = Cliente.objects.get(pk=send.data["id"])
        # import pdb; pdb.set_trace()
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
        client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = client.put(reverse('auth-clients',
                              kwargs={'pk': send.data["id"]}),
                              data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetClientsToAuthorization(APITestCase):
    """Test creado para probar los listados y autorizaciones de procesos"""
    fixtures = ['data','data2','data3','address','user','client','seller']
    def setUp(self):
        self.valid_payload = {
            'name': 'julia',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            "type_specialist": "m",
            'photo': 'preview.jpg',
            'document_type': '2',
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
            "name":"Oscar Lopez",
            "document":"93923929329",
            "document_type":"2",
            "status":"0",
            "document_type_name":"Tarjeta extranjera"
        }

        # get API response
        response = client.get(reverse('authorizations-clients'))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data[0], result_expected)
