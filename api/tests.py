
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from .models import Client as Cliente
from rest_framework import status
from .serializers import ClientSerializer
# Create your tests here.


client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer zfMCmzJkLJGkVOwtQipByVSTkXOVEb')

# user = User.objects.get(username='admin')
# client.credentials(Authorization='Bearer ' + token.key)
# force_authenticate(request, user=user, token='zfMCmzJkLJGkVOwtQipByVSTkXOVEb')

class CreateNaturalClient(APITestCase):
    # Prueba para verificar la insercion de cliente natural
    def setUp(self):
        self.valid_payload = {
            'username': 'darwin',
            'nick': 'dar',
            'type_client': 'n',
            'first_name': 'darwin',
            'last_name': 'vasquez',
            'civil_state': 's',
            'password': 'intel12345',
            'confirm_password': 'intel12345',
            'birthdate': '2017-09-19',
            "address": {
                "street": "esteban camere",
                "department": "Lima",
                "province": "Lima",
                "district": "Surco"
            },
            'photo': 'test.jpg',
            'sex': 'm',
            'document_type': '1',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'activity_description': 'Loremp iptsum',
            'level_instruction': 'Superior Concluida',
            'institute': 'UNEFA',
            'profession': 'Programmer',
            'ocupation': 'i',
            'about': 'iptsum aabout',
            'commercial_group': '',
            'economic_sector': '',
            'ciiu': '1440',
            'nationality': 'Peru'
        }

    def test_create_natural_client(self):
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, 'ey')

class GetAllClients(APITestCase):
    """ Test module for GET all clients API """

    def setUp(self):
        pass

    def test_get_all_clients(self):
        # get API response
        response = client.get(reverse('clients'))
        # get data from db
        clients = Cliente.objects.all()
        serializer = ClientSerializer(clients, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
