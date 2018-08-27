from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Specialist, Countries
from rest_framework import status
from api.serializers.actors import SpecialistSerializer


client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer SPsnU4Cz3Mx50UCuLrc20mup10s0Gz')


class AccountSpecialist(APITestCase):
    """Estado de Cuenta del Especialista."""

    fixtures = ['data', 'data2', 'data3']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
        }

    def test_get_data_month(self):
        # """Solicitud invalida por no tener el username."""
        response = client.get(reverse('specialists-account'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
