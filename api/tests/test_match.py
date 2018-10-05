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
            "file": [
                {
                    "file_url": "https://20180820-21.jpg",
                    "content_type": 1
                }
                ]
            }

    def test_no_category(self):
        """No hay especialidad."""
        data = self.valid_payload.copy()
        del data["category"]
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_category(self):
        """Especialidad no existe."""
        data = self.valid_payload.copy()
        data["category"] = 50
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_subject(self):
        """No hay especialidad."""
        data = self.valid_payload.copy()
        del data["subject"]
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_file(self):
        """No hay especialidad."""
        data = self.valid_payload.copy()
        del data["file"]
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_client_credentials(self):
        """Token no es de cliente (no autorizado)."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer FEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_create_match(self):
        """Creacion Exitosa del match."""
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
