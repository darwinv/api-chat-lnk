from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from rest_framework import status
import pdb

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')

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
		