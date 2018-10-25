"""Pruebas unitarias para el CRUD de contactos no efectivos."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from datetime import datetime
from ..models import SellerContact
from rest_framework import status
# from api.serializers.actors import ClientSerializer

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')


class CreateNaturalContact(APITestCase):
    """Prueba de Registro de Contacto Natural No Efectivo."""

    fixtures = ['data', 'data2', 'data3', 'test_contact']

    # Prueba para verificar la insercion de cliente natural
    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer RCOM8gcbsOv56QFlcCJpgDENETGCLr')
        self.valid_payload = {
            'first_name': 'darwin',
            'last_name': 'vasquez',
            'type_contact': 2,
            'type_client': 'n',
            'civil_state': 's',
            'birthdate': '1990-09-19',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'sex': 'm',
            'document_type': 2,
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            'activity_description': 'Loremp iptsum',
            'level_instruction': 1,
            'institute': 'UNEFA',
            'profession': "Administrador",
            'ocupation': 1,
            "objection": [1,2],
            "latitude": "-77.0282400",
            "longitude": "-12.0431800",
            'about': 'iptsum aabout',
            'seller': 2,
            'nationality': 1,
            'residence_country': 1
        }

    def test_no_firstname(self):
        """Solicitud invalida por no tener el nombre."""
        data = self.valid_payload
        data["first_name"] = ''
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["first_name"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["last_name"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_type_contact(self):
        """Solicitud invalida por no enviar el tipo de documento."""
        data = self.valid_payload
        data["type_contact"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["type_contact"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_typecontact(self):
        """Solicitud invalida por enviar tipo de cliente desconocido."""
        data = self.valid_payload
        data['type_contact'] = 'x'
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document_type(self):
        """Solicitud invalida por no enviar el tipo de documento."""
        data = self.valid_payload
        data["document_type"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["document_type"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_document_type(self):
        """Solicitud invalida por no enviar el tipo de documento."""
        data = self.valid_payload
        data["document_type"] = "h"
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document(self):
        """Solicitud invalida por no enviar el documento."""
        data = self.valid_payload
        data["document_number"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["document_number"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        """Solicitud invalida por email incorrecto."""
        data = self.valid_payload
        data['email_exact'] = 'asdasd'
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self):
        """Solicitud invalida por no enviarl el email."""
        data = self.valid_payload
        data["email_exact"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["email_exact"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_civil_state(self):
        """Solicitud invalida por no enviar el estado civil."""
        data = self.valid_payload
        data["civil_state"] = None
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["civil_state"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["sex"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_ocupation(self):
        """Solicitud invalida por no enviar la ocupación."""
        data = self.valid_payload
        data["ocupation"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["ocupation"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_profession(self):
        """Solicitud invalida por no enviar la profesion."""
        data = self.valid_payload
        data["address"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["profession"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_birthdate(self):
        """Solicitud invalida por enviar incorrectamente la fecha."""
        data = self.valid_payload
        data['birthdate'] = '2017/09/19'
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_birthdate(self):
        """Solicitud invalida por no enviar fecha de nacimiento."""
        data = self.valid_payload
        data["birthdate"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["birthdate"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["address"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data, 'ey')

    def test_invalid_civilstate(self):
        """Solicitud invalida por enviar estado civil desconocido."""
        data = self.valid_payload
        data['civil_state'] = 't'
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_level_instruction(self):
        """Solicitud invalida por no enviar el nivel de instruccion."""
        data = self.valid_payload
        data["level_instruction"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["level_instruction"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["nationality"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_latitude(self):
        """Solicitud invalida por no enviar latitud del contacto."""
        data = self.valid_payload
        data["latitude"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["latitude"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_longitude(self):
        """Solicitud invalida por no enviar longitud del contacto."""
        data = self.valid_payload
        data["longitude"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["longitude"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_no_seller(self):
    #     """Solicitud invalida por no enviar vendedor."""
    #     data = self.valid_payload
    #     data["seller"] = ""
    #     response1 = self.client.post(
    #         reverse('contacts'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     del data["seller"]
    #     response = self.client.post(
    #         reverse('contacts'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_objection(self):
        """Solicitud invalida por no enviar el tipo de objecion."""
        data = self.valid_payload
        data["objection"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["objection"]
        response = self.client.post(
            reverse('contacts'),
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
        del data["institute"]
        response = self.client.post(
            reverse('contacts'),
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
        data["institute"] = ""
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unique_dni(self):
        """Solicitud invalida por crear un contacto con dni repetido."""
        data1 = self.valid_payload.copy()
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        data1["username"], data1["email_exact"] = 'jesus', 'jesus@mail.com'
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data1),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_non_effective(self):
        """Crear conctacto no efectivo."""
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_send_other_objection(self):
        """Enviar otra razon."""
        data = self.valid_payload
        data["other_objection"] = "Otra  razon"
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_send_only_other_objection(self):
        """Enviar solo otra razon."""
        data = self.valid_payload
        data["other_objection"] = "Otra  razon"
        del data["objection"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_effective(self):
        """Crear conctacto efectivo."""
        self.valid_payload.pop('objection')
        self.valid_payload["type_contact"] = 1
        # registro como usuario tambien
        self.valid_payload["password"] = '123456'
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response2.status_code, status.HTTP_201_CREATED)


# Prueba para verificar la insercion de cliente juridico
class CreateBussinessContact(APITestCase):
    """Prueba de Registro de Contacto Juridico."""

    fixtures = ['data', 'data2', 'data3', 'test_contact']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer RCOM8gcbsOv56QFlcCJpgDENETGCLr')
        self.valid_payload = {
            "business_name": 'Alpanet',
            "commercial_reason": "Alpanet CA",
            'type_contact': 2,
            'type_client': 'b',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            "ruc": "19231299",
            'economic_sector': 1,
            'activity_description': 'computers and programs',
            'about': 'iptsum aabout',
            'cellphone': '921471559',
            'telephone': '921471559',
            "address": {
                "street": "esteban camere",
                "department": 1,
                "province": 1,
                "district": 1
            },
            "latitude": "-77.0282400",
            "longitude": "-12.0431800",
            "seller": 2,
            "objection": [1, 2],
            "agent_firstname": "Daniel",
            "agent_lastname": "Molina",
            'position': 'manager',
            'ciiu': 2,
            'nationality': 1,
            'residence_country': 1
        }

    def test_no_business_name(self):
        """Solicitud invalida por no enviar razon social."""
        data = self.valid_payload
        data['business_name'] = None
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data['business_name']
        # del data['business_name']
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["commercial_reason"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_type_contact(self):
        """Solicitud invalida por no enviar el tipo de contacto."""
        data = self.valid_payload
        data["type_contact"] = None
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["type_contact"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["document_type"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document(self):
        """Solicitud invalida por no enviar el documento."""
        data = self.valid_payload
        data["document_number"] = None
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["document_number"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self):
        """Solicitud invalida por no enviar el email o enviarlo vacio."""
        data = self.valid_payload
        data['email_exact'] = None
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["email_exact"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        """Solicitud invalida por email incorrecto."""
        data = self.valid_payload
        data['email_exact'] = 'asdasd'
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_ruc(self):
        """Solicitud invalida por no enviar el ruc."""
        data = self.valid_payload
        data['ruc'] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["ruc"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["economic_sector"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["address"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["ciiu"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["agent_lastname"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["agent_firstname"]
        response = self.client.post(
            reverse('contacts'),
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
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        del data["position"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unique_ruc(self):
        """Solicitud invalida tener ruc repetido."""
        data1 = self.valid_payload.copy()
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        data1["username"], data1["email_exact"] = 'jesus', 'jesus@mail.com'
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data1),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        # del data["telephone"]
        # del data["cellphone"]
        del data["activity_description"]
        # del data["about"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        # data["telephone"] = ""
        # data["cellphone"] = ""
        data["activity_description"] = ""
        # data["about"] = ""
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_latitude(self):
        """Solicitud invalida por no enviar latitud del contacto."""
        data = self.valid_payload
        data["latitude"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["latitude"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_longitude(self):
        """Solicitud invalida por no enviar longitud del contacto."""
        data = self.valid_payload
        data["longitude"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["longitude"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_no_seller(self):
    #     """Solicitud invalida por no enviar vendedor."""
    #     data = self.valid_payload
    #     data["seller"] = ""
    #     response1 = self.client.post(
    #         reverse('contacts'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     del data["seller"]
    #     response = self.client.post(
    #         reverse('contacts'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_objection(self):
        """Solicitud invalida por no enviar el tipo de objecion."""
        data = self.valid_payload
        data["objection"] = ""
        response1 = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        del data["objection"]
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_busines_non_effective(self):
        """Crea cliente juridico de manera exitosa."""
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_send_only_other_objection(self):
    #     """Enviar solo otra razon."""
    #     data = self.valid_payload
    #     data["other_objection"] = "Otra  razon"
    #     del data["objection"]
    #     response = self.client.post(
    #         reverse('contacts'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_effective(self):
        """Crear conctacto efectivo."""
        self.valid_payload.pop('objection')
        self.valid_payload["type_contact"] = 1
        # registro como usuario tambien
        self.valid_payload["password"] = '123456'
        response = self.client.post(
            reverse('contacts'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class GetContacts(APITestCase):
    """Devolver data de contactos."""
    fixtures = ['data', 'data2', 'data3', 'test_contact']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer RCOM8gcbsOv56QFlcCJpgDENETGCLr')

    def test_get_contacts(self):
        """Devolver Contactos."""
        hoy = datetime.today()
        SellerContact.objects.filter(seller=2).update(created_at=hoy)
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetContactsFilterDate(APITestCase):
    """Devolver data de contactos."""

    fixtures = ['data', 'data2', 'data3', 'test_contact']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer RCOM8gcbsOv56QFlcCJpgDENETGCLr')

    def test_get_filter_contacts(self):
        """Devolver Contactos."""
        # hoy = datetime.today()
        # SellerContact.objects.filter(seller=2).update(created_at=hoy)
        response = self.client.get(reverse('contacts-filter'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)

    def test_get_filter_no_effective_contacts(self):
        """Devolver Contactos No efectivos."""
        data = {"type_contact": 2}
        response = self.client.get(reverse('contacts-filter'), data)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_get_filter_effective_contacts(self):
        """Devolver Contactos No efectivos."""
        data = {"type_contact": 1}
        response = self.client.get(reverse('contacts-filter'), data)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_get_filter_with_date_contacts(self):
        """Devolver Contactos No efectivos."""
        data = {"date_start": '2018-08-20',
                "date_end": '2018-08-25'}
        response = self.client.get(reverse('contacts-filter'), data)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_get_filter_with_date_contacts_e(self):
        """Devolver Contactos No efectivos."""
        data = {"type_contact": 1, "date_start": '2018-08-20',
                "date_end": '2018-08-25'}
        response = self.client.get(reverse('contacts-filter'), data)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_get_filter_with_date_contacts_ne(self):
        """Devolver Contactos No efectivos."""
        data = {"type_contact": 2, "date_start": '2018-08-14',
                "date_end": '2018-08-20'}
        response = self.client.get(reverse('contacts-filter'), data)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class DetailObjectionsNotEfecctive(APITestCase):
    """Detalle de Contacto."""

    fixtures = ['data', 'data2', 'data3', 'test_contact']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer RCOM8gcbsOv56QFlcCJpgDENETGCLr')
        self.contact = 1

    def test_get_detail(self):
        """Obtener detalle de manera exitosa."""
        response = self.client.get(reverse('objections-contact',
                                           kwargs={'pk': self.contact}),
                                   format='json')
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetObjections(APITestCase):
    """Devolver listado de objeciones."""

    fixtures = ['data', 'data2', 'data3']

    def setUp(self):
        pass

    def test_get_all_objectios(self):
        """Get objections."""
        response = client.get(reverse('objections'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
