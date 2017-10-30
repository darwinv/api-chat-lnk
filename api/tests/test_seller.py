from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Seller
from rest_framework import status
from ..serializers import SellerSerializer
import pdb

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer zfMCmzJkLJGkVOwtQipByVSTkXOVEb')


class GetSellers(APITestCase):
    fixtures = ['data']
    def setUp(self):
        self.valid_payload = {
			"id_zone": "2",
			"id_username": "olopezTestPrimer",
			"id_nick": "whatever",
			"id_password": "123456",
			"id_first_name": "oscar",
			"id_last_name": "lopez",
			"id_email_exact": "mai@mail.scom",
			"id_telephone": "55443254",
			"id_cellphone": "32534323134325",
			"id_document_type": "0",
			"id_code": "23245445235",
			"id_document_number": "3143254325",
			"id_ruc": "132514325323"
		}



    def test_get_all_specialists(self):
        # get API response
        response = client.get(reverse('specialists'))
        # get data from db
        specialists = Seller.objects.all()
        serializer = SellerSerializer(specialists, many=True)

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # no funciona la prueba debido a que para
    def test_get_associates_by_main(self):
        pass
