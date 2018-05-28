"""Pruebas unitarias para las consultas."""
import json
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
# from api.models import SpecialistMessageList
from api.models import QueryPlansAcquired
from api.models import Query
# Create your tests here.

client = APIClient()
client.credentials(
    HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')  # Api Admin


class ListCategoriesClient(APITestCase):
    """Prueba devolver especialidades por consulta hecha del cliente."""

    fixtures = ['data', 'data2', 'data3', 'test_query']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer HhaMCycvJ5SCLXSpEo7KerIXcNgBSt')

    def test_get_list_by_client_whitout_id(self):
        """404 clien_id not found."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        response = client.get(reverse('queries-client'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_list_by_client(self):
        """Devolver categorias ordenadas por ultimo msj."""
        response = self.client.get(reverse('queries-client'))
        self.assertEqual(response.data[0]['status_message'], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ListQueryMessagesByCategory(APITestCase):
    """Devolver Mensajes y Consultas del cliente por especialidad."""

    fixtures = ['data', 'data2', 'data3', 'test_chat']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer kEphPGlavEforKavpDzuZSgK0zpoXS')

    def test_get_list_by_client_chat(self):
        """Estatus 200."""
        category = 8
        response = self.client.get(reverse('query-chat-client', kwargs={'pk': category}))
        # import pdb; pdb.set_trace()
        # self.assertEqual(response.data['results'][0]['message']['viewed'], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ListQueryMessagesByClient(APITestCase):
    """Devolver Mensajes y Consultas del especialista por cliente."""

    fixtures = ['data', 'data2', 'data3', 'test_chat']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer FEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')

    def test_get_chat_by_client(self):
        """Estatus 200."""
        client = 15
        response = self.client.get(reverse('query-chat-specialist', kwargs={'pk': client}))
        # self.assertEqual(response.data['results'][0]['message']['viewed'], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateQuery(APITestCase):
    """Prueba para crear consulta."""

    fixtures = ['data', 'data2', 'data3', 'test_query']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer HhaMCycvJ5SCLXSpEo7KerIXcNgBSt')
        self.valid_payload = {
            "title": "Pago de Impuestos",
            "category": 24,
            "message": [{
                "message": "primera consulta",
                "msg_type": "q",
                "content_type": 1,
                "file_url": ""
                },
                {
                "message": "",
                "msg_type": "q",
                "content_type": "1",
                "file_url": "img.png"
                }
            ],
        }

    def test_no_title(self):
        """Solicitud invalida por no enviar el titulo."""
        data = self.valid_payload
        del data["title"]
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_category(self):
        """Solicitud invalida por no enviar la especialidad."""
        data = self.valid_payload
        del data["category"]
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_message(self):
        """Solicitud invalida por no enviar un mensaje a la consulta."""
        data = self.valid_payload
        del data["message"]
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_activeplan(self):
        """No posee plan activo."""
        QueryPlansAcquired.objects.filter(client_id=5).update(is_active=False)
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_availablequeries(self):
        """Solicitud Invalida, no posee consultas."""
        QueryPlansAcquired.objects.filter(client_id=5).update(available_queries=0)
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_client_credentials(self):
        """Token no es de cliente (no autorizado)."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer FEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_contentype_file(self):
        """Verificar que el mensaje a guardar corresponde al tipo de contenido de archivo."""
        self.valid_payload["message"][0]["content_type"] = '1'
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # al enviar un mensaje de tipo archivo, la url no puede estar vacia
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_contentype_message(self):
        """Verificar que el mensaje a guardar corresponde al tipo de contenido de mensaje."""
        self.valid_payload["message"][0]["message"] = ""
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # al enviar un mensaje no puede estar vacio, mientras la el content_type
        # sea 1
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_query(self):
        """Creacion Exitosa de la consulta."""
        q = QueryPlansAcquired.objects.get(is_chosen=True, client_id=5)
        before_post_queries = q.available_queries
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        qq = QueryPlansAcquired.objects.get(is_chosen=True, client_id=5)
        after_post_queries = qq.available_queries
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(before_post_queries - 1, after_post_queries)


class ResponseSpecialistQuery(APITestCase):
    """Respuesta del especialista a la consulta."""

    fixtures = ['data', 'data2', 'data3', 'test_query']

    # put a query
    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer FEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')
        self.valid_payload = {
            "message": [{
                "message": "respuesta a consulta",
                "msg_type": "a",
                "content_type": "0",
                "file_url": "",
                "message_reference": 1
                },
                {
                "message": "",
                "msg_type": "a",
                "content_type": 2,
                "file_url": "img.png"
                }
            ]
        }

    def test_invalid_queryid(self):
        """Solicitud Invalida por no existir la consulta."""
        response = self.client.put(
            reverse('query-specialist', kwargs={'pk': 11}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_message(self):
        """Solicitud invalida por no enviar un mensaje de respuesta."""
        data = self.valid_payload
        del data["message"]
        response = self.client.put(
            reverse('query-specialist', kwargs={'pk': 1000}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_contentype_file(self):
        """Verificar que el mensaje a guardar corresponde al tipo de contenido de archivo."""
        self.valid_payload["message"][0]["content_type"] = '1'
        response = self.client.put(
            reverse('query-specialist', kwargs={'pk': 1000}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # al enviar un mensaje de tipo archivo, la url no puede estar vacia
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_contentype_message(self):
        """Verificar que el mensaje a guardar corresponde
         al tipo de contenido de mensaje."""
        self.valid_payload["message"][0]["message"] = ""
        response = self.client.put(
            reverse('query-specialist', kwargs={'pk': 1000}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # al enviar un mensaje no puede estar vacio, mientras
        # la el content_type sea 1
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_reference(self):
        """Envio de respuesta con reference_id inexistente."""
        self.valid_payload["message"][0]["message_reference"] = 5000
        response = self.client.put(
            reverse('query-specialist', kwargs={'pk': 1000}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_permissions(self):
        """Credenciales incorrectas."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer HhaMCycvJ5SCLXSpEo7KerIXcNgBSt')
        response = self.client.put(
            reverse('query-specialist', kwargs={'pk': 1000}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # Permisos incorrectos
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_query(self):
        """Respuesta exitosa del especialista."""
        # import pdb; pdb.set_trace()
        response = self.client.put(
            reverse('query-specialist', kwargs={'pk': 1000}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        query_status = Query.objects.get(pk=1000)
        self.assertEqual(4, int(query_status.status))
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class GetSpecialistMessages(APITestCase):
    """Prueba para devolver el plan activo y elegido de un determinado cliente"""

    fixtures = ['data', 'data2', 'data3', 'test_getspecialistmessages']

    def setUp(self):
        """Setup."""
        pass

    def test_get_list_messages_token_specialist(self):
        """Obtener resultado 200."""
        #se provee un token de especialista el cuel tiene   mensajes pendientes de responders
        self.client.credentials(HTTP_AUTHORIZATION='Bearer rRNQmSvkyHvi80qkYplRvLmckV3DYy')
        response = self.client.get(reverse('specialists-list-messages'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetMessageByQuery(APITestCase):
    """Prueba para devolver mensajes de un Query"""

    fixtures = ['data', 'data2', 'data3', 'test_query']

    def setUp(self):
        """Setup."""
        pass

    def test_get_message(self):
        """Obtener resultado 200."""
        #obtiene mensajes de query
        response = client.get(
            reverse('query-messages', kwargs={'pk': 1000}),)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_message_404(self):
        """Obtener resultado 404."""
        #obtiene mensajes de query
        response = client.get(
            reverse('query-messages', kwargs={'pk': 111}),)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
