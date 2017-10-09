from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Specialist
from rest_framework import status
from ..serializers import SpecialistSerializer
import pdb

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer zfMCmzJkLJGkVOwtQipByVSTkXOVEb')

class CreateSpecialist(APITestCase):
    fixtures = ['data']
    def setUp(self):
        self.valid_payload = {
            'username': 'julia',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            "type_specialist": "m",
            "address": {
                "street": "jupiter 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
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

    def test_invalid_names(self):
        data = self.valid_payload
        del data['last_name']
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_category(self):
        data = self.valid_payload
        data['category'] = 'Exploracion Espacial'
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_type_specialist(self):
        data = self.valid_payload
        data['type_specialist'] = 'r'
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_names(self):
        data = self.valid_payload
        data["last_name"] = ""
        data["first_name"] = ""
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_specialist(self):
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response.data, 'ey')
class UpdateSpecialistCase(APITestCase):
    fixtures = ['data']
    def setUp(self):
        self.valid_payload = {
            'username': 'julia',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            "type_specialist": "m",
            "address": {
                "street": "camere 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
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

        # self.assertEqual(self.resp.data["id"], 'ey')

    def test_can_update_specialist(self):
        send = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        data={'nick': 'eecih'}
        print(send)
        self.valid_payload["nick"] = "juiol"
        response = self.client.put(
            reverse('specialist-detail', kwargs={'pk': send.data["id"]}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data["nick"], 'ey')


    def test_can_change_address(self):
        data_address = {
            "address": {
                "street": "jupiter 208",
                "department": 1,
                "province": 1,
                "district": 1
            }
          }

        # agregar el especialista por defecto
        send = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        # crear direccion nueva
        data={'address': data_address["address"]}

        # actualizar la direccion del especialista
        response = self.client.put(
            reverse('specialist-detail', kwargs={'pk': send.data["id"]}),
            data, format='json'
        )

        self.assertEqual(response.data['id'], send.data["id"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # veririficar que se actualizo la direccion
        print (data['address']['street'])
        print (send.data["address"]['street'])
        self.assertEqual(data['address']['street'], response.data["address"]['street'])

class GetSpecialistCase(APITestCase):
    fixtures = ['data']
    def setUp(self):
        self.valid_payload = {
            'username': 'julia',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            "type_specialist": "m",
            "address": {
                "street": "camere 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
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



    def test_get_all_specialists(self):
        # get API response
        response = client.get(reverse('specialists'))
        # get data from db
        specialists = Specialist.objects.all()
        serializer = SpecialistSerializer(specialists, many=True)

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # no funciona la prueba debido a que para
    def test_get_associates_by_main(self):
        fixtures = ['data']
        data_first_associate = {
            'username': 'maria',
            'nick': 'maria',
            'password': 'intel12345',
            "first_name": "maria",
            "last_name": "sanz",
            "type_specialist": "a",
            "address": {
                "street": "camere 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'preview.jpg',
            'document_type': '2',
            'document_number': '0099900',
            'email_exact': 'mariasanz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            "ruc": "9999",
            "business_name": "agropatria",
            "payment_per_answer": 2.2,
            "category": 1
        }

        data_second_associate = {
            'username': 'jose',
            'nick': 'jose',
            'password': 'intel12345',
            "first_name": "jose",
            "last_name": "lopez",
            "type_specialist": "a",
            "address": {
                "street": "camere 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'preview.jpg',
            'document_type': '2',
            'document_number': '00880088',
            'email_exact': 'joselopez@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            "ruc": "88888",
            "business_name": "agropatria",
            "payment_per_answer": 2.2,
            "category": 1
        }

        # agregamos los asociados
        send_associate1 = self.client.post(
            reverse('specialists'),
            data=json.dumps(data_first_associate),
            content_type='application/json'
        )
        send_associate2 = self.client.post(
            reverse('specialists'),
            data=json.dumps(data_second_associate),
            content_type='application/json'
        )
        # agregar el especialista por defecto
        send = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        url = "{}?main_specialist={}".format(reverse('specialists'),send.data["id"])
        response = client.get(url)
        self.assertEqual(Specialist.objects.filter(category__name=send.data["category"]).exclude(type_specialist='m').count(),
                                                   response.data["count"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class DeleteSpecialistCase(APITestCase):
    fixtures = ['data']

    def setUp(self):
        self.valid_payload = {
            'username': 'maria',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            "type_specialist": "m",
            "address": {
                "street": "camere 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
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

    def test_delete_specialist(self):
        send = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(send.status_code, status.HTTP_201_CREATED)

        response = self.client.delete(
            reverse('specialist-detail', kwargs={'pk': send.data["id"]}),
            None, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
