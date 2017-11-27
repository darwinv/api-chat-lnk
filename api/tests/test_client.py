"""Pruebas unitarias para el CRUD de clientes."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Client as Cliente
from rest_framework import status
from api.serializers.actors import ClientSerializer
# Create your tests here.

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')

# user = User.objects.get(username='admin')
# client.credentials(Authorization='Bearer ' + token.key)
# force_authenticate(request, user=user, token='zfMCmzJkLJGkVOwtQipByVSTkXOVEb')

# Prueba para verificar la insercion de cliente natural


class CreateNaturalClient(APITestCase):
    """Prueba de Registro de Cliente Natural."""

    fixtures = ['data', 'data2']

    # Prueba para verificar la insercion de cliente natural
    def setUp(self):
        """Setup."""
        self.valid_payload = {
            'username': 'darwin',
            'password': 'intel12345',
            'nick': 'dar',
            'type_client': 'n',
            'first_name': 'darwin',
            'last_name': 'vasquez',
            'civil_state': 's',
            'birthdate': '2017-09-19',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'sex': 'm',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'activity_description': 'Loremp iptsum',
            'level_instruction': 1,
            'institute': 'UNEFA',
            'profession': "Administrador",
            'ocupation': '0',
            'about': 'iptsum aabout',
            'ciiu': '1440',
            'nationality': 1
        }

    # responder error al enviar email invalido
    def test_invalid_email(self):
        """Solicitud invalida por email incorrecto."""
        data = self.valid_payload
        data['email_exact'] = 'asdasd'
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self):
        """Solicitud invalida por no enviarl el email."""
        data = self.valid_payload
        del data["email_exact"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_firstname(self):
        """Solicitud invalida por no tener el nombre."""
        data = self.valid_payload
        del data["first_name"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_lastname(self):
        """Solicitud invalida por no tener el apellido."""
        data = self.valid_payload
        del data["last_name"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_username(self):
        """Solicitud invalida por no tener el username."""
        data = self.valid_payload
        del data["username"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_sex(self):
        """Solicitud invalida por no enviar el sexo."""
        data = self.valid_payload
        del data["sex"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_civil_state(self):
        """Solicitud invalida por no enviar el estado civil."""
        data = self.valid_payload
        del data["civil_state"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_nick(self):
        """Solicitud invalida por no tener enviar el nick."""
        data = self.valid_payload
        del data["nick"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_password(self):
        """Solicitud invalida por no tener enviar el password."""
        data = self.valid_payload
        del data["password"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_address(self):
        """Solicitud invalida por no tener enviar el password."""
        data = self.valid_payload
        del data["address"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_ciiu(self):
        """Solicitud invalida por no enviar el ciiu."""
        data = self.valid_payload
        del data["ciiu"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_profession(self):
        """Solicitud invalida por no enviar la profesion."""
        data = self.valid_payload
        del data["profession"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_ocupation(self):
        """Solicitud invalida por no enviar la profesion."""
        data = self.valid_payload
        del data["ocupation"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_countries(self):
        """Solicitud invalida por enviar codigo de pais inexistente."""
        data = self.valid_payload
        data['nationality'] = 500
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, 'ey')

    def test_invalid_typeclient(self):
        """Solicitud invalida por enviar tipo de cliente desconocido."""
        data = self.valid_payload
        data['type_client'] = 'x'
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_civilstate(self):
        """Solicitud invalida por enviar estado civil desconocido."""
        data = self.valid_payload
        data['civil_state'] = 't'
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_birthdate(self):
        """Solicitud invalida por enviar incorrectamente la fecha."""
        data = self.valid_payload
        data['birthdate'] = '2017/09/19'
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_birthdate(self):
        """Solicitud invalida por no enviar fecha de nacimiento."""
        data = self.valid_payload
        del data["birthdate"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        del data["telephone"]
        del data["cellphone"]
        del data["activity_description"]
        del data["level_instruction"]
        del data["about"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        # self.assertEqual(response.data, 'ey')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_natural_client(self):
        """Solicitud valida."""
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # self.assertEqual(response.data, 'ey')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# Prueba para verificar la insercion de cliente juridico
class CreateBussinessClient(APITestCase):
    """Test Para Crear Persona juridica."""

    fixtures = ['data', 'data2']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            'username': 'alpanet',
            'nick': 'alpanet',
            'type_client': 'b',
            'password': 'intel12345',
            "business_name": 'Alpanet',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            "ruc": "19231299",
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'activity_description': 'computers and programs',
            "agent_firstname": "Daniel",
            "agent_lastname": "Molina",
            'position': 'manager',
            'about': 'iptsum aabout',
            'economic_sector': 1,
            'ciiu': '1240',
            'nationality': 1
        }

    def test_empty_bussiness_fields(self):
        """Solicitud invalida por no enviar apellido de representante."""
        data = self.valid_payload
        # del data['position']
        del data['ruc']
        # del data['business_name']
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        del data["telephone"]
        del data["cellphone"]
        del data["activity_description"]
        del data["about"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        # self.assertEqual(response.data, 'ey')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_economic_sector(self):
        """Solicitud invalida por enviar sector economico invalida."""
        data = self.valid_payload
        data['economic_sector'] = "nada"
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bussines_client(self):
        """Crea cliente juridico de manera exitosa."""
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class GetDetailClient(APITestCase):
    """Detalle del Cliente."""

    fixtures = ['data', 'data2', 'data3']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            'username': 'darwin',
            'password': 'intel12345',
            'nick': 'dar',
            'type_client': 'n',
            'first_name': 'darwin',
            'last_name': 'vasquez',
            'civil_state': 's',
            'birthdate': '2017-09-19',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'sex': 'm',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'activity_description': 'Loremp iptsum',
            'level_instruction': 1,
            'institute': 'UNEFA',
            'profession': "Administrador",
            'ocupation': '0',
            'about': 'iptsum aabout',
            'ciiu': '1440',
            'nationality': 1
        }

    def test_get_client(self):
        """Prueba para obtener detalle del cliente."""
        send = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        response = client.get(reverse('client-detail',
                                      kwargs={'pk': send.data["id"]}),
                                              format='json')
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class GetAllClients(APITestCase):
    """ Test module for GET all clients API """
    fixtures = ['data','data2','data3']
    def setUp(self):
        pass

    def test_get_all_clients(self):
        # get API response
        # client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = client.get(reverse('clients'))
        # get data from db
        clients = Cliente.objects.all()
        serializer = ClientSerializer(clients, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
