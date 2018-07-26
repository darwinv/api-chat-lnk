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
    """Test module for Activate Plan by API API.""" # comentar en español ojo

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetPlans(APITestCase):
    """Devolver el listado de todos los planes."""

    fixtures = ['data', 'data2', 'data3']

    def setUp(self):
        """Setup."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')

    def test_get_list(self):
        """Obtener resultado 200 de la lista."""
        response = self.client.get(reverse('plans'), format='json')
        import pdb; pdb.set_trace()
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
        response = self.client.get(reverse('client-plans')+'?client_id=11', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetDetailPlan(APITestCase):
    """Prueba para devolver informacion de un plan"""
    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']

    def setUp(self):
        """Setup."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')

    def test_get_list(self):
        """Obtener resultado 200 de la lista."""
        response = self.client.get(reverse('client-plans-detail', args=(3,))+'?client_id=11', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetClientPlansAllList(APITestCase):
    """Prueba para devolver listado de planes al cliente"""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']

    def setUp(self):
        """Setup."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')

    def test_get_list(self):
        """Obtener resultado 200 de la lista."""
        response = self.client.get(reverse('client-plans-all'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetClientPlansShareEmpowerList(APITestCase):
    """Prueba para devolver listado de clientes compartidos facultados"""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']

    def setUp(self):
        """Setup."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')

    def test_get_list(self):
        """Obtener resultado 200 de la lista."""
        response = self.client.get(reverse('client-plans-share-empower',
            kwargs={'pk': 22}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UpdatePlanSelect(APITestCase):
    """Prueba para actualizar el plan activo de un cliente"""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']


    def setUp(self):
        """Setup."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer OPwVhxW656ASCPCjjGwgrSTXcjzzUJ')

    def test_put_plan_incorrect(self):
        """Actualizar de manera correscta."""
        # se busca un plan cuyo id no existe

        data = {'is_chosen': 1,
                'client_id': 5}

        response = self.client.put(
            reverse('chosen-plan-edit',
                    kwargs={'pk': 50000}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_plan_correct(self):
        """Actualizar el plan activo de manera exitosa."""
        data = {'is_chosen': 1}

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

class PutChosemPlanClient(APITestCase):
    """Prueba para actualizar el plan elegido de un determinado cliente"""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']

    def setUp(self):
        """Setup."""
        pass

    def test_put_chosenplan_token_clientWithPlans(self):
        """Obtener resultado 200."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer OPwVhxW656ASCPCjjGwgrSTXcjzzUJ')
        response = self.client.get(reverse('chosen-plan-edit', kwargs={'pk': 3}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

class CreateTransferPlan(APITestCase):
    """Prueba para transferir un plan"""
    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']

    def setUp(self):
        """Setup."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer OPwVhxW656ASCPCjjGwgrSTXcjzzUJ')

    def test_post_data_email_not_client(self):
        """Obtener resultado 200."""
        data = {
            "email_receiver": "test.user23@mail.com",
            "acquired_plan": 22
        }
        response = self.client.post(reverse('client-plans-transfer'), format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_data_email_client(self):
        """Obtener resultado 200."""
        data = {
            "email_receiver": "jefeti@pympack.com.pe",
            "acquired_plan": 22
        }
        response = self.client.post(reverse('client-plans-transfer'), format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MakeSharePlan(APITestCase):
    """Prueba para compartir un plan"""
    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']

    def setUp(self):
        """Setup."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer OPwVhxW656ASCPCjjGwgrSTXcjzzUJ')

    def test_post_data_email_success(self):
        """Obtener resultado 200."""
        data = {
            "acquired_plan": 22,
            "client":[
                {
                    "email_receiver": "jefeti@pympack.com.pe",
                    "count": 1
                },
                {
                    "email_receiver": "jefeti2@pympack.com.pe",
                    "count": 2
                }
            ]

        }
        response = self.client.post(reverse('client-plans-share'), format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_data_to_many_query(self):
        """Obtener resultado 400 demasiadas consultas."""
        data = {
            "acquired_plan": 22,
            "client":[
                {
                    "email_receiver": "jefeti2@pympack.com.pe",
                    "count": 10000
                }
            ]

        }
        response = self.client.post(reverse('client-plans-share'), format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_data_to_many_query2(self):
        """Obtener resultado 400 demasiadas consultas x2."""
        data = {
            "acquired_plan": 22,
            "client":[
                {
                    "email_receiver": "jefeti@pympack.com.pe",
                    "count": 5
                },
                {
                    "email_receiver": "jefeti2@pympack.com.pe",
                    "count": 5
                }
            ]

        }
        response = self.client.post(reverse('client-plans-share'), format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_data_email_myself(self):
        """Obtener resultado 200."""
        data = {
            "acquired_plan": 22,
            "client":[
                {
                    "email_receiver": "clientejosue@mail.com",
                    "count": 2
                }
            ]
        }
        response = self.client.post(reverse('client-plans-empower'), format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class MakeEmpowerPlan(APITestCase):
    """Prueba para facultar un plan"""
    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer OPwVhxW656ASCPCjjGwgrSTXcjzzUJ')

    def test_post_data_email(self):
        """Obtener resultado 200."""
        data = {
            "acquired_plan": 22,
            "client":[
                {
                    "email_receiver": "jefeti@pympack.com.pe",
                },
                {
                    "email_receiver": "jefeti2@pympack.com.pe"
                }
            ]
        }

        response = self.client.post(reverse('client-plans-empower'), format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_data_email_myself(self):
        """Obtener resultado 200."""
        data = {
            "acquired_plan": 22,
            "client":[
                {
                    "email_receiver": "clientejosue@mail.com"
                }
            ]
        }
        response = self.client.post(reverse('client-plans-empower'), format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_data_email_already(self):
        """email ya esta siento facultado con este plan."""
        data = {
            "acquired_plan": 22,
            "client":[
                {
                    "email_receiver": "cliente_no_existe@mail.com"
                }
            ]
        }
        response = self.client.post(reverse('client-plans-empower'),
                                    format='json', data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_data_email_exists_already(self):
        """email ya esta siento facultado con este plan. (cliente no existe)"""
        data = {
            "acquired_plan": 22,
            "client":[
                {
                    "email_receiver": "cliente_extra@mail.com"
                }
            ]
        }
        response = self.client.post(reverse('client-plans-empower'), format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CreatePlansNonBillable(APITestCase):
    """Crearle planes no factuables a vendedor."""

    fixtures = ['data', 'data2', 'data3', 'test_plan']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            "quantity": 2,
            "query_plans": 2,
            "seller": 19,
            "number_month": 6
        }

    def test_no_quantity(self):
        """Sin Cantidad."""
        data = self.valid_payload.copy()
        data["quantity"] = ""
        response = client.post(reverse('plans-nonbillable'),
                               format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_query_plans(self):
        """Sin plan de consulta."""
        data = self.valid_payload.copy()
        data["query_plans"] = ""
        response = client.post(reverse('plans-nonbillable'),
                               format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_seller(self):
        """Sin vendedor."""
        data = self.valid_payload.copy()
        data["seller"] = ""
        response = client.post(reverse('plans-nonbillable'),
                               format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_number_month(self):
        """Sin numero de mes."""
        data = self.valid_payload.copy()
        data["number_month"] = ""
        response = client.post(reverse('plans-nonbillable'),
                               format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_plans(self):
        """Crearle planes no Facturables"""
        data = self.valid_payload.copy()
        response = client.post(reverse('plans-nonbillable'),
                               format='json', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class GetPromocionalPlans(APITestCase):
    """Devolver  los  planes promocionales de un vendedor."""

    fixtures = ['data', 'data2', 'data3', 'test_promotional_plans']

    def setUp(self):
        """Setup."""
        # credenciales de vendedor
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer kEphPGlavEforKavpDzuZSgK0zpoXS')

    def test_get_seller_plans(self):
        """devolver todos los planes pertenecientes al vendedor."""
        response = self.client.get(reverse('seller-plans-nonbillable'))
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetPromocionalPlans(APITestCase):
    """Devolver  los  planes promocionales de un vendedor."""

    fixtures = ['data', 'data2', 'data3', 'test_promotional_plans']

    def setUp(self):
        """Setup."""
        # credenciales de vendedor
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer kEphPGlavEforKavpDzuZSgK0zpoXS')

    def test_get_seller_plans(self):
        """devolver todos los planes pertenecientes al vendedor."""
        response = self.client.get(reverse('seller-plans-nonbillable'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetCheckEmailForOperationPlans(APITestCase):
    """Devolver 404 si no existe, devuelve 200 si existe y 400 status si 
    no es valido para operacion."""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'oauth2']

    def setUp(self):
        """Setup."""
        # credenciales de vendedor
        self.valid_payload = {
            "type_operation": 2,
            "email_receiver": "jperez@mail.com",
            "acquired_plan": 22,
            'client_id':11
        }    

    def test_get_check_no_exist(self):
        """Get check if client exist in operation manage 404"""
        response = client.get(reverse('client-email-check-operation'), self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_check_exist(self):
        """Get check if client exist in operation manage 200"""
        self.valid_payload["email_receiver"] = "jefeti@pympack.com.pe"
        response = client.get(reverse('client-email-check-operation'), self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_check_allready_no_exist(self):
        """Get check if client exist in operation manage 400 no creado pero ya existe"""
        self.valid_payload["email_receiver"] = "cliente_no_existe@mail.com"
        response = client.get(reverse('client-email-check-operation'), self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_check_allready_exist(self):
        """Get check if client exist in operation manage 400 creado y ya existe"""
        self.valid_payload["email_receiver"] = "cliente_extra@mail.com"
        response = client.get(reverse('client-email-check-operation'), self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_check_myself(self):
        """Get check if client exist in operation manage 400 creado y ya existe"""
        self.valid_payload["email_receiver"] = "clientejosue@mail.com"
        response = client.get(reverse('client-email-check-operation'), self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
