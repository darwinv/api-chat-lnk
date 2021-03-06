"""Pruebas unitarias para el CRUD de clientes."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Client as Cliente, Countries
from rest_framework import status
from api.serializers.actors import ClientSerializer
# Create your tests here.

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')

# user = User.objects.get(username='admin')
# client.credentials(Authorization='Bearer ' + token.key)
# force_authenticate(request, user=user, token='zfMCmzJkLJGkVOwtQipByVSTkXOVEb')

# Prueba para verificar la insercion de cliente natural


class CreateNaturalClient(APITestCase):
    """Prueba de Registro de Cliente Natural."""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan']

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
            'birthdate': '1991-09-19',
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
            'code_telephone': 18,
            'cellphone': '921471559',
            'code_cellphone': 1,
            'activity_description': 'Loremp iptsum',
            'level_instruction': 1,
            'institute': 'UNEFA',
            'profession': "Administrador",
            'ocupation': 1,
            'about': 'iptsum aabout',
            'ciiu': 2,
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

    def test_invalidlength_password(self):
        """Solicitud invalida por clave menor de 6 caracteres."""
        data = self.valid_payload
        data['password'] = '12345'
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
        data['address'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data['address']
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_street(self):
        """Solicitud invalida por no enviar calle."""
        data = self.valid_payload
        data['address']['street'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data['address']['street']
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_department(self):
        """Solicitud invalida por no enviar departamento."""
        data = self.valid_payload
        data['address']['department'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data['address']['department']
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_province(self):
        """Solicitud invalida por no enviar provincia."""
        data = self.valid_payload
        data['address']['province'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data['address']['province']
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_district(self):
        """Solicitud invalida por no enviar distrito."""
        data = self.valid_payload
        data['address']['district'] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data['address']['district']
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_foreign_address(self):
        """Solicitud valida con dirrecion de otro pais."""
        data = self.valid_payload
        data["residence_country"] = 4
        del data["address"]
        # se agrega la direccion para ese pais
        data["foreign_address"] = "lorem pias ipmasjdn kjajsdk iasjd"
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_foreign_code(self):
        """Verificar el codigo creado anteceda el ISO de su Nacionalidad."""
        data = self.valid_payload
        data["nationality"] = 4
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cliente.objects.get(pk=response.data['client_id']).code[:3],
                         Countries.objects.get(
                            pk=data["nationality"]).iso_code + "1")

    def test_no_foreign_address(self):
        """Solicitud invalida al borrar la direccion pero enviar residencia de otro pais."""
        data = self.valid_payload
        data["residence_country"] = 4
        del data["address"]
        # se agrega la direccion para ese pais
        data["foreign_address"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["foreign_address"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
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

    def test_underage_birthdate(self):
        """Solicitud Invalida por ser menor de edad."""
        data = self.valid_payload.copy()
        data["birthdate"] = '2008-10-12'
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
        data["document_type"] = None
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

    def test_no_type_client(self):
        """Solicitud invalida por no enviar el tipo de documento."""
        data = self.valid_payload
        data["type_client"] = ""
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["type_client"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_uniqueness_document(self):
        """Solicitud invalida por ser cliente y crear un dni repetido."""
        data1 = self.valid_payload.copy()
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # cambio usuario y correo, dejando solo el tipo de documento
        data1["username"], data1["email_exact"] = 'jesus', 'jesus@mail.com'
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data1),
            content_type='application/json'
        )
        # cambio solo el tipo de documento para cerciorarse del exito.
        data2 = data1.copy()
        data2["username"], data2["email_exact"] = 'jesus1', 'jesus1@mail.com'
        data2["document_type"] = 1
        response2 = self.client.post(
            reverse('clients'),
            data=json.dumps(data2),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_no_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        del data["telephone"]
        del data["cellphone"]
        del data["activity_description"]
        del data["about"]
        del data["ciiu"]
        del data["nick"]
        del data["code_cellphone"]
        del data["code_telephone"]
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_null_nick(self):
        """Nick es null."""
        data = self.valid_payload
        data["nick"] = None
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empower_plan(self):
        """Create client con plan facultado."""
        data = self.valid_payload
        data["username"] = "cliente_no_existe@mail.com"
        data["email_exact"] = "cliente_no_existe@mail.com"

        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_transfer_plan(self):
        """Create client con plan transferido."""
        data = self.valid_payload
        data["username"] = "cliente_no_existe_transfer@mail.com"
        data["email_exact"] = "cliente_no_existe_transfer@mail.com"

        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_share_plan(self):
        """Create client con plan compartido."""
        data = self.valid_payload
        data["username"] = "cliente_no_existe_share@mail.com"
        data["email_exact"] = "cliente_no_existe_share@mail.com"

        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)




    # def test_blank_optionals(self):
    #     """Solicitud valida ya que no valida campos opcionales."""
    #     data = self.valid_payload
    #     data["nick"] = ""
    #
    #     response = self.client.post(
    #         reverse('clients'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        data["telephone"] = ""
        data["cellphone"] = ""
        data["activity_description"] = ""
        data["about"] = ""
        data["ciiu"] = ""
        data["nick"] = ""
        data["code_cellphone"] = ""
        data["code_telephone"] = ""
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_natural_client(self):
        """Solicitud valida."""
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



class UpdateNaturalClient(APITestCase):
    """Prueba de Actualizacion de Cliente Natural."""

    fixtures = ['data', 'data2', 'data3', 'test_plan']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            "first_name":"oscar",
            "last_name":"lopez",
            "nick":"lopez",
            "telephone":"1234567",
            "cellphone":"1237652",
            "residence_country":1,
            "address":{
                "street": "surco",
                "department": 1,
                "province": 1,
                "district": 1
            }
        }

    def test_from_internal_country(self):
        """actualizacion datos residente nacional"""
        data = self.valid_payload

        response = client.put(
            reverse('client-detail', args=(5,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_from_external_country(self):
        """actualizacion datos residente internacional"""
        data = self.valid_payload
        data["residence_country"] = 2
        data["foreign_address"] = "San antonio del Tachira"
        response = client.put(
            reverse('client-detail', args=(5,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_field_required(self):
        """actualizacion datos solo requeridos"""
        data = self.valid_payload
        del data['nick']
        del data['telephone']
        del data['cellphone']

        response = client.put(
            reverse('client-detail', args=(5,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_optional_field(self):
        """actualizacion datos requeridos, opcionakes vacios"""
        data = self.valid_payload
        data['nick'] = ""
        data['telephone'] = ""
        data['cellphone'] = ""

        response = client.put(
            reverse('client-detail', args=(5,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_void_requerired_field(self):
        """actualizacion datos con requeridos vacios"""
        data = self.valid_payload
        data['first_name'] = ""
        data['last_name'] = ""
        data['residence_country'] = ""
        data['address'] = ""

        response = client.put(
            reverse('client-detail', args=(5,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_requerired_field(self):
        """actualizacion datos con requeridos"""
        data = self.valid_payload
        del data['first_name']
        del data['last_name']
        del data['residence_country']
        del data['address']

        response = client.put(
            reverse('client-detail', args=(5,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # def test_nick_to_long(self):
    #     """actualizacion datos con nick largo"""
    #     data = self.valid_payload
    #     data['nick'] = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    #
    #     response = client.put(
    #         reverse('client-detail', args=(5,)),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)


# Prueba para verificar la insercion de cliente juridico
class CreateBusinessClient(APITestCase):
    """Test Para Crear Persona juridica."""

    fixtures = ['data', 'data2', 'data3']

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
            'code_telephone': 18,
            'cellphone': '921471559',
            'code_cellphone': 1,
            'activity_description': 'computers and programs',
            "agent_firstname": "Daniel",
            "agent_lastname": "Molina",
            'position': 'manager',
            'about': 'iptsum aabout',
            'economic_sector': 1,
            'ciiu': 1,
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

    def test_no_address(self):
        """Solicitud invalida por no enviar direccion."""
        data = self.valid_payload

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

    def test_invalid_ciiu(self):
        """Solicitud invalida por no enviar el ciiu."""
        data = self.valid_payload
        data['ciiu'] = 9000
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
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

    def test_uniqueness_ruc(self):
        """Invalida por ser juridico y crear un ruc existente a ese pais."""
        data1 = self.valid_payload.copy()
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        data1["username"], data1["email_exact"] = 'jesus', 'jesus@mail.com'
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data1),
            content_type='application/json'
        )
        data2 = data1.copy()
        data2["username"], data1["email_exact"] = 'juan', 'juan@mail.com'
        data2["residence_country"] = 3
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalidlength_password(self):
        """Solicitud invalida por clave menor de 6 caracteres."""
        data = self.valid_payload
        data['password'] = '12345'
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
        del data["code_cellphone"]
        del data["code_telephone"]
        del data["nick"]
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
        data["code_cellphone"] = ""
        data["code_telephone"] = ""
        data["nick"] = ""
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

    def test_no_ruc_on_foreign_residence(self):
        """Solicitud invalida por no enviar el ruc con pais extranjero."""
        data = self.valid_payload
        data['ruc'] = ""
        data['residence_country'] = 2
        data['foreign_address'] = "lorem iptsum"
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_foreign_address(self):
        """Solicitud invalida por no enviar direccion foranea cuando reside en el extranjero."""
        data = self.valid_payload
        data['residence_country'] = 2
        response1 = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

    def test_foreign_code(self):
        """Verificar el codigo creado anteceda el ISO de su Nacionalidad."""
        data = self.valid_payload
        data["nationality"] = 4
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cliente.objects.get(pk=response.data['client_id']).code[:3],
                         Countries.objects.get(
                            pk=data["nationality"]).iso_code + "1")

    def test_null_nick(self):
        """Nick es null."""
        data = self.valid_payload
        data["nick"] = None
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bussines_client(self):
        """Crea cliente juridico de manera exitosa."""
        response = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class UpdateBunissesClient(APITestCase):
    """Prueba de Actualizacion de Cliente Natural."""

    fixtures = ['data', 'data2', 'data3', 'test_plan']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            "commercial_reason":"Cocoro",
            "nick":"lopez",
            "telephone":"1234567",
            "cellphone":"1237652",
            "residence_country":1,
            "address":{
                "street": "surco",
                "department": 1,
                "province": 1,
                "district": 1
            }
        }

    def test_from_internal_country(self):
        """actualizacion datos residente nacional"""
        data = self.valid_payload

        response = client.put(
            reverse('client-detail', args=(11,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_from_external_country(self):
        """actualizacion datos residente internacional"""
        data = self.valid_payload
        data["country"] = "2"
        data["foreign_address"] = "San antonio del Tachira"

        response = client.put(
            reverse('client-detail', args=(11,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_field_required(self):
        """actualizacion datos solo requeridos"""
        data = self.valid_payload
        del data['nick']
        del data['telephone']
        del data['cellphone']

        response = client.put(
            reverse('client-detail', args=(11,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_optional_field(self):
        """actualizacion datos requeridos, opcionakes vacios"""
        data = self.valid_payload
        data['nick'] = ""
        data['telephone'] = ""
        data['cellphone'] = ""

        response = client.put(
            reverse('client-detail', args=(11,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_void_requerired_field(self):
        """actualizacion datos con requeridos vacios"""
        data = self.valid_payload
        data['commercial_reason'] = ""
        data['residence_country'] = ""
        data['address'] = ""

        response = client.put(
            reverse('client-detail', args=(11,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_requerired_field(self):
        """actualizacion datos con requeridos"""
        data = self.valid_payload
        del data['commercial_reason']
        del data['residence_country']
        del data['address']

        response = client.put(
            reverse('client-detail', args=(11,)),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # def test_nick_to_long(self):
    #     """actualizacion datos con nick largo"""
    #     data = self.valid_payload
    #     data['nick'] = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    #
    #     response = client.put(
    #         reverse('client-detail', args=(11,)),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

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
                'birthdate': '1992-09-19',
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
                'code_telephone': 18,
                'cellphone': '921471559',
                'code_cellphone': 1,
                'activity_description': 'Loremp iptsum',
                'level_instruction': 1,
                'institute': 'UNEFA',
                'profession': "Administrador",
                'ocupation': 1,
                'about': 'iptsum aabout',
                'ciiu': 2,
                'nationality': 1,
                'residence_country': 1
        }

    def test_get_client(self):
        """Prueba para obtener detalle del cliente."""
        send = self.client.post(
            reverse('clients'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        response = client.get(reverse('client-detail',
                                      kwargs={'pk': send.data['client_id']}),
                              format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAllClients(APITestCase):
    """Test module for GET all clients API."""

    fixtures = ['data', 'data2', 'data3']
    def setUp(self):
        pass

    def test_get_all_clients(self):
        # get API response
        response = client.get(reverse('clients'))
        # get data from db
        clients = Cliente.objects.all()
        serializer = ClientSerializer(clients, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class SendRecoveryCode(APITestCase):
    """Test module for GET all clients API."""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan']
    def setUp(self):
        pass

    def test_gest_user_by_code_recovery(self):
        # get API response
        data = {'email':'jefeti@pympack.com.pe'}
        response = client.post(reverse('send-code-password'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_error_empty_data(self):
        # no envio de email
        response = client.post(reverse('send-code-password'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_bad_email(self):
        # envio mal correo
        data = {'email':'jefeti12345@pympack.com.pe'}
        response = client.post(reverse('send-code-password'), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CheckData(APITestCase):
    """Chequear si existe algun cliente con  esos datos"""
    fixtures = ['data', 'data2', 'data3', 'test_client']

    def setUp(self):
        pass

    def test_check_ruc(self):
        """chequear si existe  el ruc."""
        data = {"ruc": "123456789", "role": 2}

        response = client.get(reverse('check-data'), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_no_role(self):
        """chequear si no existe rol."""
        data = {"ruc": "123456789"}
        response = client.get(reverse('check-data'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_email(self):
        """chequear si existe el correo."""
        # data = {"role": 2, "email_exact": "darwinio_vasqz@gmail.com"}
        data = {"role": 2, "email_exact": "darwinio_vasqz@gmail.com"}
        response = client.get(reverse('check-data'), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_DNI(self):
        """chequera si existe el dni."""
        data = {"role": 2, "document_type": 1,
                "document_number": "20122984"}
        response = client.get(reverse('check-data'), data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_passport(self):
        """chequera si existe el pasaporte."""
        data = {"role": 2, "document_type": 2,
                "document_number": "20122984"}

        response = client.get(reverse('check-data'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_foreign_card(self):
        """chequear si existe el carnet de extranjeria."""
        data = {"role": 2, "document_type": 3,
                "document_number": "20122984"}
        response = client.get(reverse('check-data'), data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetUserByRecoverCode(APITestCase):
    """Test module for GET all clients API."""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'test_recovery_password']

    def setUp(self):
        pass

    def test_gest_user_by_code_recovery(self):
        # get API response
        data = {'email':'jefeti@pympack.com.pe', 'code':'WEY4D1'}
        response = client.get(reverse('valid-code-password'), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 5)

    def test_error_empty_data(self):
        # no envio de data
        response = client.get(reverse('valid-code-password'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_bad_email(self):
        # envio data erronea
        data = {'email':'jefeti12345@pympack.com.pe','code': 'XYZ123'}
        response = client.get(reverse('valid-code-password'), data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class GetClientByUsername(APITestCase):
    """Test module for GET all clients API."""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'test_recovery_password']

    def setUp(self):
        pass

    def test_gest_user(self):
        # get API response
        response = client.get(reverse('client-detail-username', args=("jefeti@pympack.com.pe",)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdatePasswordByRecoverCode(APITestCase):
    """Test module for Update password user API."""

    fixtures = ['data', 'data2', 'data3', 'test_chosen_plan', 'test_recovery_password']
    def setUp(self):
        pass

    def test_update_password_by_recovery(self):
        # get API response
        data = {'password':'123456', 'code':'WEY4D1'}

        response = client.put(reverse('reset-password-recovery', args=(5,)), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 5)

    def test_error_empty_data(self):
        # no envio de data
        response = client.put(reverse('reset-password-recovery', args=(111,)))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_bad_email(self):
        # envio data erronea
        data = {'password': '123456', 'code': 'XYZ123'}
        response = client.put(reverse('reset-password-recovery', args=(111,)),
                              data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdatePasswordClientNatural(APITestCase):
    """Actualizar perfil del Cliente."""
    fixtures = ['data', 'data2', 'data3', 'test_client']

    def setUp(self):
        self.data = {
            "old_password": '123456',
            "password": '123459'
        }
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer FEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')

    def test_invalid_permission(self):
        """Credenciales no permitidas."""
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION='ZZk2avXwe09l8lqS3zTc0Q3Qsl7yZZ')
        response = client.put(reverse('update-password',
                              args=(5,)), data=json.dumps(self.data),
                              content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_old_password(self):
            """Password actual invalida."""
            self.data["old_password"] = '123468'
            response = client.put(reverse('update-password',
                                  args=(5,)), data=json.dumps(self.data),
                                  content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_password(self):
        """Actualizar contraseña."""
        response = client.put(reverse('update-password',
                              args=(5,)), data=json.dumps(self.data),
                              content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetNotificationOnBadge(APITestCase):
    """Notificacion on badge."""

    fixtures = ['data', 'data2', 'data3', 'test_notification']

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer FEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')

    def test_get_badge(self):
        """Badge para el cliente."""
        response = self.client.get(reverse('get-badge'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["queries_pending"], 2)
        self.assertEqual(response.data["match_pending"], 1)


class UpdateEmail(APITestCase):
    """Test module for put email user API."""

    fixtures = ['data', 'data2', 'data3', 'test_plan']
    
    def setUp(self):
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer user3GlavEforKavpDzuZSgK0zpoXS')

    def test_update_email(self):
        # put email
        data = { 'client_id':3,
                'email_exact':'olopez@mail.com',
                'password':'123456'
            }

        response = self.client.put(reverse('update-email', args=(3,)), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email_exact'], data['email_exact'])

    def test_update_email_no_valid(self):
        # put email incorrecto
        data = { 'client_id':3,
                'email_exact':'olopmail.com',
                'password':'123456'
            }

        response = self.client.put(reverse('update-email', args=(3,)), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_no_email(self):
        # put no email
        data = { 'client_id':3,
                'password':'123456'
            }

        response = self.client.put(reverse('update-email', args=(3,)), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_no_data(self):
        # put no data
        data = { 'client_id':3
            }
        response = self.client.put(reverse('update-email', args=(3,)), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_email_no_valid(self):
        # put email repeat
        data = { 'client_id':3,
                'email_exact':'jose@mail.com',
                'password':'123456'
            }
        response = self.client.put(reverse('update-email', args=(3,)), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_email_bad_password(self):
        # put email bad password
        data = { 'client_id':3,
                'email_exact':'olopezdeveloper@mail.com',
                'password':'654321'
            }

        response = self.client.put(reverse('update-email', args=(3,)), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
