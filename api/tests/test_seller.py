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

    fixtures = ['data', 'data2', 'data3']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            'username': 'darwin',
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
            'ciiu': 1,
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
        data["last_name"] = ''
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response1 = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["last_name"]
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_firstname(self):
        """Solicitud invalida por no tener el nombre."""
        data = self.valid_payload
        data["first_name"] = ''
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response1 = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["first_name"]
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_nick(self):
        """Solicitud invalida por no tener el nick."""
        data = self.valid_payload
        del data["nick"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response1 = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
            )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self):
        """Solicitud invalida por no enviarl el email."""
        data = self.valid_payload
        data["email_exact"] = ""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response1 = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["email_exact"]
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_nationality(self):
        """Solicitud invalida por no enviar el pais de nacionalidad."""
        data = self.valid_payload
        data["nationality"] = ""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response1 = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["nationality"]
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document(self):
        """Solicitud invalida por no enviar el documento."""
        data = self.valid_payload
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        data["document_number"] = ""
        response1 = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["document_number"]
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document_type(self):
        """Solicitud invalida por no enviar el tipo de documento."""
        data = self.valid_payload
        data["document_type"] = ""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response1 = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["document_type"]
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_address(self):
        """Solicitud invalida por no enviar la direccion."""
        data = self.valid_payload
        data["address"] = ""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response1 = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["address"]
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_residence_country(self):
        """Solicitud invalida no enviar pais de residencia."""
        data = self.valid_payload
        data['residence_country'] = ""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response1 = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["residence_country"]
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

    def test_foreign_address(self):
        """Solicitud valida al borrar la direccion pero enviar residencia de otro pais."""
        data = self.valid_payload
        data["residence_country"] = 4
        del data["address"]
        # se agrega la direccion para ese pais
        data["foreign_address"] = "lorem pias ipmasjdn kjajsdk iasjd"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_foreign_address(self):
        """Solicitud valida al borrar la direccion pero enviar residencia de otro pais."""
        data = self.valid_payload
        data["residence_country"] = 4
        del data["address"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        # se agrega la direccion para ese pais
        data["foreign_address"] = ""
        response1 = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["foreign_address"]
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_null_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        data["cellphone"] = None
        data["ruc"] = None
        data["ciiu"] = None
        data["telephone"] = None
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('sellers'),
            data=json.dumps(data),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        data["cellphone"] = ""
        data["ruc"] = ""
        data["ciiu"] = ""
        data["telephone"] = ""
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
