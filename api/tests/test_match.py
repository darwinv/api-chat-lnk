"""Pruebas unitarias para los match."""
import json
import os
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

client = APIClient()
client.credentials(
    HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')  # Api Admin


class RequestMatch(APITestCase):
    """Prueba para crear un match por parte del cliente."""

    fixtures = ['data', 'data2', 'data3', 'test_match']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer HhaMCycvJ5SCLXSpEo7KerIXcNgBSt')
        self.valid_payload = {
            "category": 8,
            "subject": "Quiero demandar a la sunat",
            "files": [
                {
                    "file_url": "https://20180820-21.jpg",
                    "content_type": 1
                }
                ]
            }

    def test_create_match(self):
        """Creacion Exitosa del match."""
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
