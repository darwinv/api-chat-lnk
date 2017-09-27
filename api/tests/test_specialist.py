from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Specialist
from rest_framework import status
from ..serializers import SpecialistSerializer

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer zfMCmzJkLJGkVOwtQipByVSTkXOVEb')

class CreateSpecialistCase(APITestCase):
    def setUp(self):
        self.valid_payload = {
            'username': 'julia',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            'confirm_password': 'intel12345',
            "type_specialist": "m",
            "address": {
                "street": "jupiter 209",
                "department": "Lima",
                "province": "Lima",
                "district": "Surco"
            },
            'photo': 'preview.jpg',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            "ruc": "2009918312",
            "bussiness_name": "agropatria",
            "payment_per_answer": 2.2,
            "category": "Agroindustria"
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

class GetSpecialistCase(APITestCase):
    def setUp(self):
        pass
    def test_get_all_specialists(self):
        # get API response
        response = client.get(reverse('specialists'))
        # get data from db
        specialists = Specialist.objects.all()
        serializer = SpecialistSerializer(specialists, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
