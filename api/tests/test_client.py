from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Client as Cliente
from rest_framework import status
from api.serializers.actors import ClientSerializer
# Create your tests here.

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')

# user = User.objects.get(username='admin')
# client.credentials(Authorization='Bearer ' + token.key)
# force_authenticate(request, user=user, token='zfMCmzJkLJGkVOwtQipByVSTkXOVEb')

# Prueba para verificar la insercion de cliente natural
class CreateNaturalClient(APITestCase):
    fixtures = ['data','data2']
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
            'birthdate': '2017-09-19',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'test.png',
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
            'nationality': 1
        }
    # responder error al enviar email invalido
    def test_invalid_email(self):
        data = self.valid_payload
        data['email_exact']='asdasd'
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, 'ey')
    # def test_invalid_photo_extension(self):
    #     data = self.valid_payload
    #     data['photo'] = 'tex.xcf'
    #     response = self.client.post(
    #         reverse('clients'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_invalid_photo_url(self):
    #     data = self.valid_payload
    #     data['photo'] = 'tex'
    #     response = self.client.post(
    #         reverse('clients'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, 'ey')

    def test_invalid_countries(self):
        data = self.valid_payload
        data['nationality'] = 500
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, 'ey')

    def test_invalid_typeclient(self):
        data = self.valid_payload
        data['type_client'] = 'x'
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_civilstate(self):
        data = self.valid_payload
        data['civil_state'] = 'o'
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_invalid_birthdate(self):
        data = self.valid_payload
        data['birthdate'] = '2017/09/19'
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_natural_client(self):
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # self.assertEqual(response.data, 'ey')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# Prueba para verificar la insercion de cliente juridico
class CreateBussinessClient(APITestCase):
    fixtures = ['data','data2']
    def setUp(self):
        self.valid_payload = {
            'username': 'alpanet',
            'nick': 'alpanet',
            'type_client': 'b',
            'password': 'intel12345',
            "business_name": 'Alpanet',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'test.jpg',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'activity_description': 'computers and programs',
            "agent_firstname": "Daniel",
            "agent_lastname": "Molina",
            'position': 'manager',
            'about': 'iptsum aabout',
            'economic_sector': 1,
            'ciiu': '1240',
            'nationality': 1
        }

    def test_empty_bussiness_fields(self):
        data = self.valid_payload
        del data['agent_lastname']
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_economic_sector(self):
        data = self.valid_payload
        data['economic_sector'] = "nada"
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bussines_client(self):
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



class GetDetailClient(APITestCase):
    fixtures = ['data','data2','data3']
    def setUp(self):
        self.valid_payload = {
            'username': 'darwin',
            'nick': 'dar',
            'type_client': 'n',
            'first_name': 'darwin',
            'last_name': 'vasquez',
            'civil_state': 's',
            'password': 'intel12345',
            'birthdate': '2017-09-19',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'test.jpg',
            'sex': 'm',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'activity_description': 'Loremp iptsum',
            'level_instruction': 1,
            'institute': 'UNEFA',
            'profession': 'Administrador',
            'ocupation': '0',
            'about': 'iptsum aabout',
            'ciiu': '1440',
            'nationality': 1
        }

    def test_get_client(self):
        send = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        response = client.get(reverse('client-detail',
                         kwargs={'pk': send.data["id"]}),format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class GetAllClients(APITestCase):
    """ Test module for GET all clients API """
    fixtures = ['data','data2','data3']
    def setUp(self):
        pass

    def test_get_all_clients(self):
        # get API response
        # client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = client.get(reverse('clients'))
        # get data from db
        clients = Cliente.objects.all()
        serializer = ClientSerializer(clients, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
