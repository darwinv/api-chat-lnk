from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Specialist, Countries
from rest_framework import status
from api.serializers.actors import SpecialistSerializer


client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')


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
            'document_type': 1,
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        del data["nick"]
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_null_nick(self):
        """Nick es null."""
        data = self.valid_payload
        data["nick"] = None
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_names(self):
        """Solicitud invalida al enviar los nombres vacios."""
        data = self.valid_payload
        data["last_name"] = ""
        data["first_name"] = ""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_uniqueness_document(self):
        """Solicitud invalida por ser especialista y crear un dni repetido."""
        data1 = self.valid_payload.copy()
        self.client.credentials(
             HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        data1["username"], data1["email_exact"] = 'jesus', 'jesus@mail.com'
        data1["ruc"], data1["type_specialist"] = data1["ruc"] + "2", "a"
        response1 = self.client.post(
            reverse('specialists'),
            data=json.dumps(data1),
            content_type='application/json'
        )
        data2 = data1.copy()
        data2["username"], data2["email_exact"] = 'jauna', 'jauna@mail.com'
        data2["ruc"], data2["type_specialist"] = data2["ruc"] + '1', 'a'
        data2["document_type"] = 2
        response2 = self.client.post(
            reverse('specialists'),
            data=json.dumps(data2),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_uniqueness_ruc(self):
        """Solicitud invalida por ser especialista y crear un ruc repetido."""
        data1 = self.valid_payload.copy()
        self.client.credentials(
             HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        data1["username"], data1["email_exact"] = 'jesus', 'jesus@mail.com'
        data1["document_number"] = data1["document_number"] + "1"
        data1["type_specialist"] = "a"
        response1 = self.client.post(
            reverse('specialists'),
            data=json.dumps(data1),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

    def test_foreign_code(self):
        """Verificar el codigo creado anteceda el ISO de su Nacionalidad."""
        data = self.valid_payload
        data["nationality"] = 4
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["code"][:3],
                         Countries.objects.get(
                            pk=data["nationality"]).iso_code + "E")

    def test_create_specialist(self):
        """Creacion de especialistas."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_specialist_foreign(self):
        """Creacion de especialistas extranjero."""
        data = self.valid_payload
        data['residence_country'] = 3
        data['foreign_address'] = "Calle buena pinta - Casa 66á´05"
        data['ruc'] = ""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.post(
            reverse('specialists'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_specialist_foreign_without(self):
        """Validacion de especialistas extranjero sin foreign_address."""
        data = self.valid_payload
        self.test_create_specialist_foreign()  # Llamado a crear especialista extranjero

        data['foreign_address'] = ""

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = client.get(reverse('specialist-detail',
                              kwargs={'pk': self.specialist}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetNotificationOnBadgeMainSpecialist(APITestCase):
    """Notificacion redondela especialista principal."""

    fixtures = ['data', 'data2', 'data3', 'test_notification']

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer FEk2avXwe09lk2avXwe09k2avX')

    def test_get_badge(self):
        """Badge para el cliente."""
        response = self.client.get(reverse('get-badge'))
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["queries_pending"], 2)
        self.assertEqual(response.data["match_pending"], 1)


class GetNotificationOnBadgeAsocSpecialist(APITestCase):
    """Notificacion redondela especialista asociado."""

    fixtures = ['data', 'data2', 'data3', 'test_notification']

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer FEk2avXwe09lk2avXweFEk2avXwe09')

    def test_get_badge(self):
        """Badge para el cliente."""
        response = self.client.get(reverse('get-badge'))
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["queries_pending"], 1)
        self.assertEqual(response.data["match_pending"], 0)


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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')

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
        self.assertEqual(response.data['id'], send.data["id"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # veririficar que se actualizo la direccion
        # print (data['address']['street'])
        # print (send.data["address"]['street'])
        self.assertEqual(
            data['address']['street'], response.data["address"]['street'])

class GetSpecialists(APITestCase):
    fixtures = ['data', 'data2', 'data3']
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
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = self.client.get(reverse('specialists'))
        # get data from db
        specialists = Specialist.objects.all()
        serializer = SpecialistSerializer(specialists, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # no funciona la prueba debido a que para
    def test_get_associates_by_main(self):
        fixtures = ['data', 'data2', 'data3']
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
            "category": 1,
            "nationality": 1,
            "residence_country": 1
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
            "category": 1,
            "nationality": 1,
            "residence_country": 1
        }

        # agregamos los asociados
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')

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
        url = "{}?main_specialist={}".format(reverse('specialists'),send.data["id"])
        response = self.client.get(url)

        self.assertEqual(Specialist.objects.filter(category=send.data["category"]).exclude(type_specialist='m').count(),
                                                   response.data["count"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DeleteSpecialist(APITestCase):
    fixtures = ['data', 'data2', 'data3']

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
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
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


class GetAsociateSpecialistByQuery(APITestCase):
    """Devolver Especialistas asociados"""

    fixtures = ['data', 'data2', 'data3', 'test_getspecialistmessages']

    def setUp(self):
        """Setup."""
        pass

    def test_get_specialists(self):
        """Obtener resultado 200."""
        #obtiene especialistas asociados

        client.credentials(HTTP_AUTHORIZATION='Bearer rRNQmSvkyHvi80qkYplRvLmckV3DYy')
        data = {'query':1}
        response = client.get(reverse('specialists-asociate'), data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetAsociateSpecialist(APITestCase):
    """Devolver Especialistas asociados"""

    fixtures = ['data', 'data2', 'data3', 'test_getspecialistmessages']

    def setUp(self):
        """Setup."""
        pass

    def test_get_specialists(self):
        """Obtener resultado 200."""
        #obtiene especialistas asociados

        client.credentials(HTTP_AUTHORIZATION='Bearer rRNQmSvkyHvi80qkYplRvLmckV3DYy')
        response = client.get(reverse('specialists-associate-category'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdatePasswordSpecialist(APITestCase):
    """Actualizar clave del especialista."""

    fixtures = ['data', 'data2', 'data3', 'test_specialist']

    def setUp(self):
        self.data = {
            "old_password": '123456',
            "password": '123459'
        }
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer vvP8pKMAULMa2qQtaTnJpx2l87nWc2')

    def test_invalid_permission(self):
        """Credenciales no permitidas."""
        self.client.credentials(
            HTTP_AUTHORIZATION='ZZk2avXwe09l8lqS3zTc0Q3Qsl7yZZ')
        response = self.client.put(reverse('update-password',
                              args=(3,)), data=json.dumps(self.data),
                              content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_old_password(self):
            """Password actual invalida."""
            self.data["old_password"] = '123468'
            response = self.client.put(reverse('update-password',
                                               args=(3,)),
                                       data=json.dumps(self.data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_password(self):
        """Actualizar contraseña."""
        response = self.client.put(reverse('update-password',
                                           args=(3,)),
                                   data=json.dumps(self.data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdateProfileSpecialist(APITestCase):
    """Actualizar perfil de especialista."""

    fixtures = ['data', 'data2', 'data3', 'test_specialist']

    def setUp(self):
        self.valid_payload = {
            "first_name": 'juan',
            "last_name": 'delgado',
            "business_name": "barca",
            "telephone": "921099231",
            "cellphone": "091231231",
            "address": {
                "street": "jupiter 209",
                "department": 1,
                "province": 1,
                "district": 1
            },
            "nick": "jdelg"

        }
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer vvP8pKMAULMa2qQtaTnJpx2l87nWc2')

    def test_update_profile(self):
        """Actualizar Perfil."""
        response = self.client.put(
            reverse('specialist-detail', kwargs={'pk': 3}),
            self.valid_payload, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetSpecialistByUsername(APITestCase):
    """Test module for GET all clients API."""

    fixtures = ['data', 'data2', 'data3', 'test_specialist']

    def setUp(self):
        pass

    def test_gest_user(self):
        # get API response
        client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = client.get(reverse('specialist-detail-username', args=("teresaq@tesla.com",)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
