from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
# Create your tests here.

# token = Token.objects.get(user__username='lauren')
client = APIClient()
# client.credentials(Authorization='Bearer ' + token.key)
client.force_authenticate(user=None)

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
            'birthdate': '2017-09-19',
            'photo': 'test.jpg',
            'sex': 'm',
            'document_type': '1',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'activity_description': 'Loremp iptsum',
            'level_instruction': 1,
            'institute': 'UNEFA',
            'profession': 1,
            'ocupation': 'i',
            'about': 'iptsum aabout',
            'ciiu': '1440'
        }
    def test_create_natural_client(self):
        response = client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
