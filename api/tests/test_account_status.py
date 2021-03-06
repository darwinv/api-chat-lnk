from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import ParameterSeller, SellerNonBillablePlans
from rest_framework import status
from api.serializers.actors import SpecialistSerializer
from datetime import datetime

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
        self.assertEqual(response.data["mounth"]["match_accepted"], 0)
        self.assertEqual(response.data["mounth"]["queries_category_absolved"], 0)
        self.assertEqual(response.data["mounth"]["match_declined"], 0)
        self.assertEqual(response.data["mounth"]["queries_asociate_absolved"], 0)
        self.assertEqual(response.data["mounth"]["queries_category_total"], 0)
        self.assertEqual(response.data["mounth"]["queries_main_absolved"], 0)
        self.assertEqual(response.data["mounth"]["queries_main_total"], 0)
        self.assertEqual(response.data["mounth"]["queries_asociate_total"], 0)
        self.assertEqual(response.data["mounth"]["match_total"], 0)
        self.assertEqual(response.data["mounth"]["queries_main_pending"], 0)
        self.assertEqual(response.data["mounth"]["queries_category_pending"], 0)
        self.assertEqual(response.data["mounth"]["queries_asociate_pending"], 0)


    def test_data_footer(self):
        """data del footer del especialista."""
        response = client.get(reverse('footer-specialist'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # absuelto por el mes
        self.assertEqual(response.data["month_queries_absolved"], 2)
        self.assertEqual(response.data["queries_absolved"], 5)


class AccountProfileSeller(APITestCase):
    """Estado de cuenta del Vendedor."""

    fixtures = ['data', 'data2', 'data3', 'test_account_seller']

    def setUp(self):
        """SetUp."""
        self.seller = 6
        self.hoy = datetime.now()

    def test_month_new_clients(self):
        """Traer clientes nuevos del  mes."""
        ParameterSeller.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        SellerNonBillablePlans.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["month_clients"], 2)

    def test_month_new_contacts(self):
        """Traer contactos  nuevos del mes."""
        ParameterSeller.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        SellerNonBillablePlans.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))

        self.assertEqual(response.data["month_contacts"], 3)

    def test_month_promotionals(self):
        """Traer planes promocionales entregados del mes."""
        ParameterSeller.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        SellerNonBillablePlans.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_promotionals"], 2)

    def test_month_people_purchase(self):
        """Traer cantidad de gente que compro."""
        ParameterSeller.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        SellerNonBillablePlans.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_people_purchase"], 2)

    def test_month_people_purchase_goal(self):
        """Meta de cantidad de gente que debe comprar."""
        ParameterSeller.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        SellerNonBillablePlans.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_people_purchase_goal"], 12)

    def test_month_contacts_goal(self):
        """Traer meta de contactos del mes."""
        ParameterSeller.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        SellerNonBillablePlans.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_contacts_goal"], 10)

    def test_month_new_clients_goal(self):
        """Traer meta de clientes nuevos del mes."""
        ParameterSeller.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        SellerNonBillablePlans.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_new_clients_goal"], 10)

    def test_month_all_promotionals(self):
        """Traer planes promocionales disponibles."""

        ParameterSeller.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        SellerNonBillablePlans.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)
        response = client.get(reverse('sellers-account',
                                      args=(self.seller,)))
        self.assertEqual(response.data["month_all_promotionals"], 8)


class AccountStatusClient(APITestCase):
    """Estado de cuenta del cliente."""

    fixtures = ['data', 'data2', 'data3', 'test_account_client']

    def setUp(self):
        """SetUp."""
        self.cliente = 3
        self.hoy = datetime.now()
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer dfsdf')

    def test_account_client(self):
        """Cliente estado de cuenta."""

        response = client.get(reverse('clients-account',
                                      args=(self.cliente,)))
        # import pdb; pdb.set_trace()
        self.assertEqual(response.data["historic"]["queries_acquired"], 6)
        self.assertEqual(response.data["historic"]["queries_absolved"], 6)
        self.assertEqual(response.data["historic"]["queries_pending"], 5)
        self.assertEqual(response.data["historic"]["available_queries"], 2)


class AccountStatusSeller(APITestCase):
    """Estado de cuenta Backend del Vendedor."""

    fixtures = ['data', 'data2', 'data3', 'test_account_seller']

    def setUp(self):
        """SetUp."""
        self.seller = 6
        self.hoy = datetime.now()
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer SellerPsnU4Cz3Mx50UCuLrc20mup10s0Gz')

    def test_month_sold_plans(self):
        """Planes vendidos en el mes."""
        SellerNonBillablePlans.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        ParameterSeller.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        response = client.get(reverse('sellers-account-back',
                                      args=(self.seller,)))

        self.assertEqual(response.data["mounth"]["month_people_purchase_goal"], 12)
        self.assertEqual(response.data["mounth"]["month_new_clients_goal"], 10)
        self.assertEqual(response.data["mounth"]["month_promotionals"], 0)
        self.assertEqual(response.data["mounth"]["month_clients"], 0)
        self.assertEqual(response.data["mounth"]["month_all_promotionals"], 6)
        self.assertEqual(response.data["mounth"]["month_contacts_goal"], 10)
        self.assertEqual(response.data["mounth"]["month_people_purchase"], 0)
        self.assertEqual(response.data["mounth"]["month_contacts"], 0)


    def test_data_footer(self):
        """footer de Vendedor."""
        SellerNonBillablePlans.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        ParameterSeller.objects.all().update(
            number_month=self.hoy.month, number_year=self.hoy.year)

        response = self.client.get(reverse('footer-seller'))
        self.assertEqual(response.data["month_promotionals"], 2)
        self.assertEqual(response.data["month_not_effective"], 0)
        self.assertEqual(response.data["month_effective"], 3)
