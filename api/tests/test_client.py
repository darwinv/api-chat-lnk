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
            'nationality': 1,
            'residence_country': 1
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
        data["email_exact"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["email_exact"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_firstname(self):
        """Solicitud invalida por no tener el nombre."""
        data = self.valid_payload
        data["first_name"] = ''
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["first_name"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_lastname(self):
        """Solicitud invalida por no tener el apellido."""
        data = self.valid_payload
        data["last_name"] = ''
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["last_name"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
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
        data["sex"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["sex"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document(self):
        """Solicitud invalida por no enviar el documento."""
        data = self.valid_payload
        data["document_number"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["document_number"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_civil_state(self):
        """Solicitud invalida por no enviar el estado civil."""
        data = self.valid_payload
        data["civil_state"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["civil_state"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_nick(self):
        """Solicitud invalida por no enviar el nick o enviarlo vacio."""
        data = self.valid_payload
        data['nick'] = ''
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_password(self):
        """Solicitud invalida por no enviar el password o enviarlo vacio."""
        data = self.valid_payload
        data['password'] = ''
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["password"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_address(self):
        """Solicitud invalida por no enviar direccion."""
        data = self.valid_payload
        data["address"]["district"] = ""
        response2 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        data["address"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["address"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_address_outside_peru(self):
        """Solicitud valida al borrar la direccion pero enviar residencia de otro pais."""
        data = self.valid_payload
        data["residence_country"] = 4
        del data["address"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
        """Solicitud invalida por no enviar la ocupación."""
        data = self.valid_payload
        data["ocupation"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["ocupation"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
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

    def test_invalid_residence_country(self):
        """Solicitud invalida por enviar codigo de pais inexistente."""
        data = self.valid_payload
        data['residence_country'] = 500
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_residence_country(self):
        """Solicitud invalida no enviar pais de residencia."""
        data = self.valid_payload
        data['residence_country'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["residence_country"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

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
        data["birthdate"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["birthdate"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_nationality(self):
        """Solicitud invalida por no enviar nacionalidad."""
        data = self.valid_payload
        data["nationality"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["nationality"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_level_instruction(self):
        """Solicitud invalida por no enviar el nivel de instruccion."""
        data = self.valid_payload
        data["level_instruction"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["level_instruction"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document_type(self):
        """Solicitud invalida por no enviar el tipo de documento."""
        data = self.valid_payload
        data["document_type"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["document_type"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        del data["telephone"]
        del data["cellphone"]
        del data["activity_description"]
        del data["about"]
        del data["ciiu"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        data["telephone"] = ""
        data["cellphone"] = ""
        data["activity_description"] = ""
        data["about"] = ""
        data["ciiu"] = ""
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_natural_client(self):
        """Solicitud valida."""
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
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
            "commercial_reason": "Alpanet CA",
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
            'nationality': 1,
            'residence_country': 1
        }

    def test_no_business_name(self):
        """Solicitud invalida por no enviar razon social."""
        data = self.valid_payload
        data['business_name'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data['business_name']
        # del data['business_name']
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_nick(self):
        """Solicitud invalida por no enviar el nick o enviarlo vacio."""
        data = self.valid_payload
        data['nick'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["nick"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_address(self):
        """Solicitud invalida por no enviar direccion."""
        data = self.valid_payload
        data["address"]["district"] = ""
        response2 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        data["address"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["address"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document(self):
        """Solicitud invalida por no enviar el documento."""
        data = self.valid_payload
        data["document_number"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["document_number"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document_type(self):
        """Solicitud invalida por no enviar el tipo de documento."""
        data = self.valid_payload
        data["document_type"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["document_type"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self):
        """Solicitud invalida por no enviar el email o enviarlo vacio."""
        data = self.valid_payload
        data['email_exact'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["email_exact"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_comercial_reason(self):
        """Solicitud invalida por no enviar el razon comercial."""
        data = self.valid_payload
        data['commercial_reason'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["commercial_reason"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_ruc(self):
        """Solicitud invalida por no enviar el ruc."""
        data = self.valid_payload
        data['ruc'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["ruc"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_economic_sector(self):
        """Solicitud invalida por no enviar el Sector Economico."""
        data = self.valid_payload
        data['economic_sector'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["economic_sector"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_ciiu(self):
        """Solicitud invalida por no enviar el ciiu."""
        data = self.valid_payload
        data['ciiu'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["ciiu"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_agent_lastname(self):
        """Solicitud invalida por no enviar el apellido del representante."""
        data = self.valid_payload
        data['agent_lastname'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["agent_lastname"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_agent_firstname(self):
        """Solicitud invalida por no enviar el apellido del representante."""
        data = self.valid_payload
        data['agent_firstname'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["agent_firstname"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_position(self):
        """Solicitud invalida por no enviar el cargo."""
        data = self.valid_payload
        data['position'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["position"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        data["telephone"] = ""
        data["cellphone"] = ""
        data["activity_description"] = ""
        data["about"] = ""
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_economic_sector(self):
        """Solicitud invalida por enviar sector economico invalido."""
        data = self.valid_payload
        data['economic_sector'] = "nada"
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_residence_country(self):
        """Solicitud invalida por enviar pais de residencia diferente a peru."""
        data = self.valid_payload
        data['residence_country'] = 4
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
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
