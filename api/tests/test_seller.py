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

    def test_no_username(self):
        """Solicitud invalida por no tener el username."""
        data = self.valid_payload
        del data["username"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_lastname(self):
        """Solicitud invalida por no tener el apellido."""
        data = self.valid_payload
        del data["last_name"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_firstname(self):
        """Solicitud invalida por no tener el nombre."""
        data = self.valid_payload
        del data["first_name"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_nick(self):
        """Solicitud invalida por no tener el nick."""
        data = self.valid_payload
        del data["nick"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self):
        """Solicitud invalida por no enviar el correo."""
        data = self.valid_payload
        del data["email_exact"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_nationality(self):
        """Solicitud invalida por no enviar el pais de nacionalidad."""
        data = self.valid_payload
        del data["nationality"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document(self):
        """Solicitud invalida por no enviar el documento."""
        data = self.valid_payload
        del data["document_number"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_address(self):
        """Solicitud invalida por no enviar la direccion."""
        data = self.valid_payload
        del data["address"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_no_residence(self):
    #     """Solicitud invalida por no enviar el pais de residencia."""
    #     data = self.valid_payload
    #     del data["residence_country"]
    #     self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
    #     response = self.client.post(
    #         reverse('sellers'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_optionals(self):
        """Solicitud valida al no enviar los campos opcionales."""
        data = self.valid_payload
        del data["cellphone"]
        del data["ruc"]
        del data["ciiu"]
        del data["telephone"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
