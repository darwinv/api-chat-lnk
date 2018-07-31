"""Test para Compras."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')


class PurchaseQueryPlans(APITestCase):
    """Caso de pruebas para Compras."""

    fixtures = ['data', 'data2', 'data3', 'test_purchase']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            "place": "BCP",
            "description": "test",
            "is_fee": True,
            "client": 5,
            "seller": 2,
            "products": [{
                "product_type": 1,
                "is_billable": True,
                "plan_id": 2,
               }]
        }

    def test_purchase_succesfull(self):
        """Compra exitosa."""
        response = client.post(reverse('purchase'),
                               data=json.dumps(self.valid_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_purchase_promotional(self):
        """Compra exitosa."""
        self.valid_payload = {
                "place": "BCP",
                "description": "test",
                "is_fee": True,
                "client": 5,
                "seller": 2,
                "products": [{
                    "product_type": 1,
                    "is_billable": False,
                    "plan_id": 2,
                   }]
            }
        response = client.post(reverse('purchase'),
                               data=json.dumps(self.valid_payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response2 = client.post(reverse('purchase'),
                                data=json.dumps(self.valid_payload),
                                content_type='application/json')

        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
