from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Specialist
from rest_framework import status
from api.serializers.actors import SpecialistSerializer
import pdb


client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')

class CreateSpecialist(APITestCase):
    """Pruebas de Crear especialista."""

    fixtures = ['data', 'data2', 'data3']

    def setUp(self):
        """Setup."""
        self.valid_payload = {
            'username': 'julia',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            "type_specialist": "m",
            "address": {
                "street": "jupiter 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'preview.jpg',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            "ruc": "2009918312",
            "business_name": "agropatria",
            "payment_per_answer": 2.2,
            "category": 1,
            "nationality": 1,
            "residence_country": 1
        }

    def test_no_username(self):
        """Solicitud invalida por no tener el username."""
        data = self.valid_payload
        del data["username"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_nick(self):
        """Solicitud invalida por no tener el nick."""
        data = self.valid_payload
        del data["nick"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_names(self):
        """Solicitud invalida por no tener el apellido o nombre."""
        data = self.valid_payload
        del data['first_name']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self):
        """Solicitud invalida por no enviar el email."""
        data = self.valid_payload
        del data['email_exact']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_document(self):
        """Solicitud invalida por no enviar el documento."""
        data = self.valid_payload
        del data['document_number']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_address(self):
        """Solicitud invalida por no enviar la direccion."""
        data = self.valid_payload
        del data['address']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_business_name(self):
        """Solicitud invalida por no enviar el nombre de la empresa."""
        data = self.valid_payload
        del data['business_name']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_category(self):
        """Solicitud invalida por no enviar una especialidad valida."""
        data = self.valid_payload
        data['category'] = 100
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_category(self):
        """Solicitud invalida por no enviar una especialidad."""
        data = self.valid_payload
        del data['category']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_ruc(self):
        """Solicitud invalida por no enviar ruc."""
        data = self.valid_payload
        del data['ruc']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_payment(self):
        """Solicitud invalida por no enviar pago por respuesta."""
        data = self.valid_payload
        del data['payment_per_answer']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_type_specialist(self):
        """Solicitud invalida por no enviar el tipo de especialista correcto."""
        data = self.valid_payload
        data['type_specialist'] = 'r'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_optionals(self):
        """Solicitud valida ya que no valida campos opcionales."""
        data = self.valid_payload
        del data["telephone"]
        del data["cellphone"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_names(self):
        """Solicitud invalida al enviar los nombres vacios."""
        data = self.valid_payload
        data["last_name"] = ""
        data["first_name"] = ""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_empty_nationality(self):
        """Solicitud invalida al no enviar sitio de residencia."""
        data = self.valid_payload
        data["nationality"] = ""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_specialist(self):
        """Creacion de especialistas."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    def test_create_specialist_foreign(self):
        """Creacion de especialistas extranjero"""
        data = self.valid_payload
        data['residence_country'] = 3
        data['foreign_address'] = "Calle buena pinta - Casa 66á´05"
        data['ruc'] = ""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_specialist_foreign_without(self):
        """Validacion de especialistas extranjero sin foreign_address"""

        data = self.valid_payload
        self.test_create_specialist_foreign()  # Llamado a crear especialista extranjero

        data['foreign_address'] = ""

        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DetailSpecialist(APITestCase):
    """Detalle de Especialista."""

    fixtures = ['data', 'data2', 'data3', 'test_address', 'test_specialist']

    def setUp(self):
        """Setup."""
        self.specialist = 3

    def test_get_detail(self):
        """Obtener detalle de manera exitosa."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = client.get(reverse('specialist-detail',
                              kwargs={'pk': self.specialist}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdateSpecialistCase(APITestCase):
    fixtures = ['data','data2','data3']
    def setUp(self):
        self.valid_payload = {
            'username': 'julia',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            "type_specialist": "m",
            "address": {
                "street": "camere 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'preview.jpg',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            "ruc": "2009918312",
            "business_name": "agropatria",
            "payment_per_answer": 2.2,
            "category": 1,
            "nationality": 1,
            "residence_country": 1
        }

        # self.assertEqual(self.resp.data["id"], 'ey')

    def test_can_update_specialist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        send = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        data = {
            'nick': 'eecih',
            "address": {
                "street": "jupiter 208",
                "department": 1,
                "province": 1,
                "district": 1
            },
            "residence_country":1,
            "ruc":2132453421
          }
        self.valid_payload["nick"] = "juiol"

        response = self.client.put(
            reverse('specialist-detail', kwargs={'pk': send.data["id"]}),
            data, format='json'
        )

        # pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data["nick"], 'ey')


    def test_can_change_address(self):
        """Poder cambiar la direccion de residencia"""
        data_address = {
            "address": {
                "street": "jupiter 208",
                "department": 1,
                "province": 1,
                "district": 1
            },
            "residence_country":1,
            "ruc":2132453421
          }

        # agregar el especialista por defecto
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        send = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        # crear direccion nueva
        data={'address': data_address["address"],
                'residence_country':data_address["residence_country"],
                'ruc':data_address["ruc"]}

        # actualizar la direccion del especialista
        response = self.client.put(
            reverse('specialist-detail', kwargs={'pk': send.data["id"]}),
            data, format='json'
        )
        #import pdb; pdb.set_trace()
        self.assertEqual(response.data['id'], send.data["id"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # veririficar que se actualizo la direccion
        print (data['address']['street'])
        print (send.data["address"]['street'])
        self.assertEqual(data['address']['street'], response.data["address"]['street'])

class GetSpecialists(APITestCase):
    fixtures = ['data','data2','data3']
    def setUp(self):
        self.valid_payload = {
            'username': 'julia',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            "type_specialist": "m",
            "address": {
                "street": "jupiter 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'preview.jpg',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            "ruc": "2009918312",
            "business_name": "agropatria",
            "payment_per_answer": 2.2,
            "category": 1,
            "nationality": 1,
            "residence_country": 1
        }



    def test_get_all_specialists(self):
        # get API response
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        response = client.get(reverse('specialists'))
        # get data from db
        specialists = Specialist.objects.all()
        serializer = SpecialistSerializer(specialists, many=True)

        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # no funciona la prueba debido a que para
    def test_get_associates_by_main(self):
        fixtures = ['data','data2','data3']
        data_first_associate = {
            'username': 'maria',
            'nick': 'maria',
            'password': 'intel12345',
            "first_name": "maria",
            "last_name": "sanz",
            "type_specialist": "a",
            "address": {
                "street": "camere 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'preview.jpg',
            'document_type': '2',
            'document_number': '0099900',
            'email_exact': 'mariasanz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            "ruc": "9999",
            "business_name": "agropatria",
            "payment_per_answer": 2.2,
            "category": 1
        }

        data_second_associate = {
            'username': 'jose',
            'nick': 'jose',
            'password': 'intel12345',
            "first_name": "jose",
            "last_name": "lopez",
            "type_specialist": "a",
            "address": {
                "street": "camere 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'preview.jpg',
            'document_type': '2',
            'document_number': '00880088',
            'email_exact': 'joselopez@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            "ruc": "88888",
            "business_name": "agropatria",
            "payment_per_answer": 2.2,
            "category": 1
        }

        # agregamos los asociados
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        send_associate1 = self.client.post(
            reverse('specialists'),
            data=json.dumps(data_first_associate),
            content_type='application/json'
        )
        send_associate2 = self.client.post(
            reverse('specialists'),
            data=json.dumps(data_second_associate),
            content_type='application/json'
        )
        # agregar el especialista por defecto
        send = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        #import pdb; pdb.set_trace()
        url = "{}?main_specialist={}".format(reverse('specialists'),send.data["id"])
        response = client.get(url)

        self.assertEqual(Specialist.objects.filter(category=send.data["category"]).exclude(type_specialist='m').count(),
                                                   response.data["count"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class DeleteSpecialist(APITestCase):
    fixtures = ['data','data2','data3']

    def setUp(self):
        self.valid_payload = {
            'username': 'julia',
            'nick': 'julia',
            'password': 'intel12345',
            "first_name": "juliana",
            "last_name": "garzon",
            "type_specialist": "m",
            "address": {
                "street": "jupiter 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
            'photo': 'preview.jpg',
            'document_type': '2',
            'document_number': '144013012',
            'email_exact': 'darwin.vasqz@gmail.com',
            'telephone': '921471559',
            'cellphone': '921471559',
            "ruc": "2009918312",
            "business_name": "agropatria",
            "payment_per_answer": 2.2,
            "category": 1,
            "nationality": 1,
            "residence_country": 1
        }

    def test_delete_specialist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')
        send = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(send.status_code, status.HTTP_201_CREATED)

        response = self.client.delete(
            reverse('specialist-detail', kwargs={'pk': send.data["id"]}),
            None, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
