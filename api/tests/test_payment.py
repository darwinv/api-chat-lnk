"""Pruebas unitarias para el CRUD de clientes."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Payment
from rest_framework import status

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')


class MakePayment(APITestCase):
    """Prueba de Crear Pagos."""

    fixtures = ['data', 'data2', 'data3', 'test_payment']

    def setUp(self):
        """SetUp."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        self.valid_payload = {
            "amount": 500,
            "operation_number": "123123-ERT",
            "observations": "opcional",
            "monthly_fee": 1,
            "payment_type": 2,
            "bank": 1
        }

    def test_make_payment(self):
        """Crear pago."""
        data = self.valid_payload
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_monthly_fee(self):
        """cuota mensual no existe."""
        data = self.valid_payload.copy()
        del data["monthly_fee"]
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_optional_observations(self):
        """Observaciones son opcionales."""
        data = self.valid_payload.copy()
        del data["observations"]
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_monthly_fee(self):
        """cuota mensual no existe."""
        data = self.valid_payload.copy()
        data["monthly_fee"] = 2
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_operation_number(self):
        """No envia numero de operacion."""
        data = self.valid_payload.copy()
        del data["operation_number"]
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_amount(self):
        """No envia numero de operacion."""
        data = self.valid_payload.copy()
        del data["amount"]
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)