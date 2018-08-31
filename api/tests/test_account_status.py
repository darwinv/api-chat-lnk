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
        """Traer data del mes del Especialista."""

        response = client.get(reverse('specialists-account',
                                      args=(self.specialist,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # absuelto por el mes
        self.assertEqual(response.data["month_queries_absolved"], 2)
        # pendientes por absolver por el mes
        self.assertEqual(response.data["month_queries_pending"], 4)
        # absueltos historico de especialidad
        self.assertEqual(response.data["queries_absolved_category"], 5)


class AccountSeller(APITestCase):
    """Estado de cuenta del Vendedor."""

    fixtures = ['data', 'data2', 'data3', 'test_account_seller']

    def setUp(self):
        """SetUp."""
        self.seller = 6

    def test_month_new_clients(self):
        """Traer clientes nuevos del  mes."""
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["month_clients"], 2)

    def test_month_new_contacts(self):
        """Traer contactos  nuevos del mes."""
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_contacts"], 3)

    def test_month_promotionals(self):
        """Traer planes promocionales entregados del mes."""
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_promotionals"], 2)

    def test_month_people_purchase(self):
        """Traer cantidad de gente que compro."""
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_people_purchase"], 2)

    def test_month_contacts_goal(self):
        """Traer meta de contactos del mes."""
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_contacts_goal"], 10)

    def test_month_new_clients_goal(self):
        """Traer meta de clientes nuevos del mes."""
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_new_clients_goal"], 10)

    def test_month_available_promotional(self):
        """Traer planes promocionales disponibles."""
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["mont_available_promotional"], 6)
