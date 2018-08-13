"""Test para Compras."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import SaleDetail
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

    def test_no_place(self):
        """Sin lugar."""
        data = self.valid_payload.copy()
        data["place"] = ""
        response = client.post(reverse('purchase'),
                               data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_client(self):
        """Cliente  obligatorio."""
        data = self.valid_payload.copy()
        data["client"] = None
        response = client.post(reverse('purchase'),
                               data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_seller(self):
        """Sin Vendedor."""
        data = self.valid_payload.copy()
        del data["seller"]
        response = client.post(reverse('purchase'),
                               data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_purchase_succesfull(self):
        """Compra exitosa."""
        response = client.post(reverse('purchase'),
                               data=json.dumps(self.valid_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PurchaseQueryPromotionalPlans(APITestCase):
    """Compra  de plan promocional."""
    fixtures = ['data', 'data2', 'data3', 'test_purchase']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            "place": "BCP",
            "description": "test",
            "is_fee": False,
            "client": 5,
            "seller": 2,
            "products": [{
                "product_type": 1,
                "is_billable": False,
                "plan_id": 2,
               }]
        }

    def test_unavailable_promotional(self):
        """planes de vendedor agotados."""
        data = self.valid_payload.copy()
        data["products"][0]["plan_id"] = 5
        response = client.post(reverse('purchase'),
                               data=json.dumps(self.valid_payload),
                               content_type='application/json')
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_promotional_for_seller(self):
        """no es un plan promocional para este vendedor."""
        data = self.valid_payload.copy()
        data["products"][0]["plan_id"] = 3
        response = client.post(reverse('purchase'),
                               data=json.dumps(data),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_promotional_repeat_client(self):
        """Compra exitosa promocional."""
        # import pdb; pdb.set_trace()
        response = client.post(reverse('purchase'),
                               data=json.dumps(self.valid_payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # print(SaleDetail.objects.all())
        response2 = client.post(reverse('purchase'),
                                data=json.dumps(self.valid_payload),
                                content_type='application/json')

        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
