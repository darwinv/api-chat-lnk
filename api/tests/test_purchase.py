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
            "description_sale": "test",
            "is_fee": True,
            "client": 5,
            "seller": 2,
            "products": [{
                "product_type": 1,
                "is_billable": True,
                "plan_id": 2,
                "discount": 0.00,
               }]
        }

    def test_purchase_succesfull(self):
        """Compra exitosa."""
        # import pdb; pdb.set_trace()
        response = client.post(reverse('purchase'),
                               data=json.dumps(self.valid_payload),
                               content_type='application/json')
        import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_purchase_with_fee(self):
        """Compra exitosa."""
        pass
