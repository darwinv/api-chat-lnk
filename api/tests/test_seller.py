"""Test para Vendedores."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Seller
from rest_framework import status
from api.serializers.actors import SellerSerializer
import pdb

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')


class CreateSeller(APITestCase):
    """Crear prueba para crear vendedor."""

    fixtures = ['data', 'data2', "data3"]

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            'username': 'darwin',
            'password': 'intel12345',
            'nick': 'dar',
            'first_name': 'darwin',
            'last_name': 'vasquez',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'ciiu': '1440',
            'ruc': '144023123',
            'nationality': 1,
            'residence_country': 1
        }

    def test_create_seller(self):
        """Solicitud valida."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class GetAllSellers(APITestCase):
    """Test module for GET all sellers API."""

    fixtures = ['data', 'data2', 'data3']


    def setUp(self):
        pass

    def test_get_all_sellers(self):
        # get API response
        response = client.get(reverse('sellers'))
        # get data from db
        sellers = Seller.objects.all()
        serializer = SellerSerializer(sellers, many=True)
        print(response.data['results'])
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
