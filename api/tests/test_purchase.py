"""Test para Compras."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.utils.tools import get_date_by_time
from api.models import QueryPlansAcquired

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')


class PurchaseQueryPlans(APITestCase):
    """Caso de pruebas para Compras."""

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            "place": "BCP",
            "description": "test",
            
        }
