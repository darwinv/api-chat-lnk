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

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            "place": "BCP",
            "description_sale": "test",
            "is_fee": True,
            "client": 1,
            "seller": 10,
            "products": [{
                "product_type": 1,
                "is_billable": True,
                "plan_id": 1,
                "description": "plan de consulta",
                "discount": 0.00,
               }]
        }

    def test_purchase_succesfull(self):
        """Compra exitosa."""
        response = client.post(reverse('purchase'),
                               data=json.dumps(self.valid_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
