"""Test para Planes."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.utils.tools import get_date_by_time
from api.models import QueryPlansAcquired

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')

class GetPlanByPIN(APITestCase):
    """Test module for GET plan deactive API."""

    fixtures = ['data', 'data2', 'data3', 'test_plan']

    def setUp(self):
        # Token de un cliente con plan activo
        client.credentials(
            HTTP_AUTHORIZATION='Bearer kEphPGlavEforKavpDzuZSgK0zpoXS')

    def test_get_plan_by_pin(self):
        """Traer Plan enviado codigo PIN Correcto."""
        self.valid_payload = {
            "plan_name": "Minipack",
            "query_quantity": 6,
            "available_queries": 6,
            "validity_months": 3,
            "expiration_date": "2018-05-14",
            "price": "700.00",
            "is_active": False,
            'is_chosen': False
        }

        # get API response
        response = client.get(reverse('activation-plan', args=('INTEL12345',)))

        self.assertEqual(response.data, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_plan_active(self):
        """Traer plan activo para activacion, FALSO
        no se pueden activar un plan activado"""

        self.valid_payload = {
            "plan_name": "Minipack",
            "query_quantity": 6,
            "available_queries": 6,
            "validity_months": 3,
            "expiration_date": "2018-05-14",
            "price": "700.00",
            "is_active": True,
            'is_chosen': False
        }

        # get API response
        response = client.get(reverse('activation-plan', args=('INTEL12345',)))

        self.assertNotEqual(response.data, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdatePlanActiveByAPI(APITestCase):
    """Test module for Activate Plan by API API."""

    fixtures = ['data', 'data2', 'data3', 'test_plan']

    def setUp(self):
        """SetUp."""
        # Token de un cliente con plan activo
        client.credentials(HTTP_AUTHORIZATION=
                           'Bearer kEphPGlavEforKavpDzuZSgK0zpoXS')

    def test_update_plan_by_pin(self):
        """Update Plan By PIN. Activacion de plan."""
        code = 'INTEL12345'

        plan_adquired = QueryPlansAcquired.objects.values('validity_months')\
            .filter(sale_detail__pin_code=code, is_active=False)[:1].get()

        expiration_date = get_date_by_time(plan_adquired['validity_months'])

        self.valid_payload = {
            "expiration_date": expiration_date.strftime('%Y-%m-%d'),
            'is_active': True
        }

        # get API response
        response = client.put(reverse('activation-plan', args=(code,)))
        # import pdb; pdb.set_trace()
        self.assertEqual(response.data['is_active'],
                         self.valid_payload['is_active'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetClientPlansList(APITestCase):
    """Prueba para devolver listado de planes al cliente"""
    # fixtures = ['data', 'data2', 'data3']

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']


    def setUp(self):
        """Setup."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')

    def test_get_list(self):
        """Obtener resultado 200 de la lista."""
        response = self.client.get(reverse('client-plans'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UpdatePlanSelect (APITestCase):
    """Prueba para actualizar el plan activo de un cliente"""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']


    def setUp(self):
        """Setup."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer OPwVhxW656ASCPCjjGwgrSTXcjzzUJ')

    def test_put_plan_incorrect(self):
        """Actualizar de manera correscta."""
        #se busca un plan cuyo id no existe

        data = {'is_chosen': 1,
                'client_id': 5}

        response = self.client.put(
            reverse('chosen-plan-edit',
                    kwargs={'pk': 50000}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_plan_correct(self):
        """Actualizar el plan activo de manera exitosa."""

        data = {'is_chosen': 1,
	            'client_id': 11}

        response = self.client.put(
            reverse('chosen-plan-edit',
                    kwargs={'pk': 2}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetSpecialistQueryCount(APITestCase):
    """Prueba para devolver los totales de consultas de un especialista """

    # fixtures = ['data', 'data2', 'data3', 'test_plan', 'oauth2']
    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']

    def setUp(self):
        """Setup."""
        pass

    def test_get_token_client(self):
        """Obtener resultado 200 de la lista."""
        # se provee un token de especialista
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer rRNQmSvkyHvi80qkYplRvLmckV3DYy')
        response = self.client.get(
            reverse('specialist-query-count'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_token_admin(self):
        """Obtener resultado 200 de la lista."""
        # se provee un token de administrador
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.get(
            reverse('specialist-query-count'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # se comento por que falta ingresar el usuario con el token al fixture data2
    def test_get_list_token_client(self):
        """Obtener resultado 200 de la lista."""
        # se provee un token erroneo
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer 9M84R1jUHHx2AZkAGb3C6OF72QM7Xh')
        response = self.client.get(
            reverse('specialist-query-count'), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class GetChosemPlanClient(APITestCase):
    """Prueba para devolver el plan activo y elegido de un determinado cliente"""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']

    def setUp(self):
        """Setup."""
        pass

    def test_get_chosenplan_token_admin(self):
        """Obtener resultado 404."""
        # se provee un token de administrador el cuel no tiene planes en el fixture
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.get(reverse('chosen-plan'), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_chosenplan_token_clientWithPlans(self):
        """Obtener resultado 200."""
        # se provee un token de cliente (id 11 en el fixture) que si posee planes en el fixture
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer OPwVhxW656ASCPCjjGwgrSTXcjzzUJ')
        response = self.client.get(reverse('chosen-plan'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_chosenplan_token_clientWithOutPlans(self):
        """Obtener resultado 404."""
        # se provee un token de cliente (id 5 en el fixture) que no posee planes en el fixture
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer 9M84R1jUHHx2AZkAGb3C6OF72QM7Xh')
        response = self.client.get(reverse('chosen-plan'), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_chosenplan_token_specialist(self):
        """Obtener resultado 404."""
        # se provee un token de especialista (id 4 en el fixture) que no posee planes en el fixture
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer rRNQmSvkyHvi80qkYplRvLmckV3DYy')
        response = self.client.get(reverse('chosen-plan'), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_chosenplan_token_clientWithPlans2(self):
        """Obtener resultado 200."""
        # se provee un token de cliente (id 11 en el fixture) que si posee planes en el fixture
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer OPwVhxW656ASCPCjjGwgrSTXcjzzUJ')

        self.valid_payload = {
            "is_active": True,
            'is_chosen': True
        }
        # get API response
        response = self.client.get(reverse('chosen-plan'), format='json')

        self.assertNotEqual(response.data, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
