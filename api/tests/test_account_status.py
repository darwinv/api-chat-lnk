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

    fixtures = ['data', 'data2', 'data3', 'test_account_specialist']

    def setUp(self):
        """Setup."""
        self.specialist = 20
        self.valid_payload = {
        }

    def test_get_data_month(self):
        # """Solicitud invalida por no tener el username."""
        response = client.get(reverse('specialists-account',
                                      args=(self.specialist,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # absuelto por el mes
        self.assertEqual(response.data["month_queries_absolved"], 2)
        # pendientes por absolver por el mes
        self.assertEqual(response.data["month_queries_pending"], 4)
        # absueltos historico de especialidad
        self.assertEqual(response.data["queries_absolved_category"], 5)
