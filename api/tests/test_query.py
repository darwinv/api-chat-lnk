from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
from django.db.models import Q
import json
from ..models import Query
from rest_framework import status
import pdb
# from ..serializers import ClientSerializer
# Create your tests here.

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer zfMCmzJkLJGkVOwtQipByVSTkXOVEb')

class GetAllQuerys(APITestCase):
    """ Test module for GET all Querys API """

    fixtures = ['data','data2','test_address','test_query']
    def setUp(self):
        self.id_client = 2
        self.id_category = 1

    # devolver todos los querys segun cliente
    def test_get_all_querys_client(self):
        # get API response
        url = "{}?client={}".format(reverse('queries'),self.id_client)
        response = client.get(url)
        # get data from db
        self.assertEqual(Query.objects.filter(client_id=self.id_client).count(), response.data["count"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_client(self):
        response = client.get(reverse('queries'))
        # get data from db
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # obtener filtradas por categoria
    def test_get_querys_client_by_category(self):
        url = "{}?client={}&category={}".format(reverse('queries'),
                                                self.id_client,
                                                self.id_category)
        response = client.get(url)
        # get data from db
        self.assertEqual(Query.objects.filter(client_id=self.id_client,
                                              category_id=self.id_category).count(),
                                              response.data["count"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_absolved_queries_by_category(self):
        url = "{}?client={}&category={}&status=absolved".format(reverse('queries'),
                                                        self.id_client,
                                                        self.id_category)
        response = client.get(url)
        self.assertEqual(Query.objects.filter(Q(status=6) | Q(status=7),
                                              category_id=self.id_category,
                                              client_id=self.id_client).count(),
                                              response.data["count"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_pending_queries_by_category(self):
        url = "{}?client={}&category={}&status=pending".format(reverse('queries'),
                                                        self.id_client,
                                                        self.id_category)
        response = client.get(url)
        self.assertEqual(Query.objects.filter(status__lte=5,
                                              category_id=self.id_category,
                                              client_id=self.id_client).count(),
                                              response.data["count"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_absolved_queries_(self):
        url = "{}?client={}&status=absolved".format(reverse('queries'),
                                                        self.id_client)
        response = client.get(url)
        self.assertEqual(Query.objects.filter(Q(status=6) | Q(status=7),
                                              client_id=self.id_client).count(),
                                              response.data["count"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_pending_queries(self):
        url = "{}?client={}&status=pending".format(reverse('queries'),
                                                        self.id_client)
        response = client.get(url)
        self.assertEqual(Query.objects.filter(status__lte=5,
                                              client_id=self.id_client).count(),
                                              response.data["count"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

#
class GetDetailQuery(APITestCase):
    fixtures = ['data','data2','test_address','test_query']
    def setUp(self):
        self.id_client = 2
        self.id_category = 1
        self.id_query = 1

    def test_get_query(self):
        response = client.get(reverse('query-detail',
                     kwargs={'pk': self.id_query }),format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_query(self):
        response = client.get(reverse('query-detail',
                     kwargs={'pk': 100 }),format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class CreateQuery(APITestCase):
    fixtures = ['data','data2','test_address','test_query']
    def setUp(self):
        self.valid_payload = {
            "title" : "Visa Solicitud",
            "message": {
                "message": "Lorem ipsum dolor sit amet,anctus e",
                "msg_type": "q",
                "media_files": []
            },
            "category": 1,
            "client": 2
        }
    # validar si el titulo esta muy largo
    def test_title_large(self):
        data = self.valid_payload
        data["title"] = "aasdsjkl asd aksd kasjd laksdjkasdl asdklasjdkasdjlkasdj"
        response = self.client.post(
            reverse('queries'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_query(self):
        response = self.client.post(
            reverse('queries'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # import pdb; pdb.set_trace()
        # self.assertEqual(response.data, "ee")
class UpdateQuery(APITestCase):
    fixtures = ['data','data2','test_address','test_query']
    def setUp(self):
        self.valid_payload = {
            "title" : "Visa Solicitud",
            "message": {
                "message": "Lorem ipsum dolor sit amet,anctus e",
                "msg_type": "q",
                "media_files": []
            },
            "category": 1,
            "client": 2
        }

    def test_add_message_to_query(self):
        send = self.client.post(
            reverse('queries'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        data={
            "message": {
            "message": "reconsulta",
            "msg_type": "q",
            "media_files": []
            }
        }
        # import pdb; pdb.set_trace()
        response = self.client.put(
            reverse('query-detail', kwargs={'pk': send.data["id"]}),
            data, format='json'
        )

        # self.assertEqual(response.data, "ee")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SkipReQuery(APITestCase):
    fixtures = ['data','data2','test_address','test_query']
    def setUp(self):
        self.id_client = 2
        self.id_category = 1
        self.id_query = 11
        self.valid_payload = {
        "status":7
        }

    def test_skip_requery(self):
        query = Query.objects.get(pk=self.id_query)
        query.status = 5
        query.save()
        response = self.client.put(
            reverse('query-detail', kwargs={'pk': self.id_query}),
            self.valid_payload, format='json'
        )
        self.assertEqual(int(response.data["status"]), 7)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateReQuery(APITestCase):
    fixtures = ['data','data2','test_address','test_query']
    def setUp(self):
        self.valid_payload = {
            "title" : "Visa Solicitud",
            "message": {
                "message": "Lorem ipsum dolor sit amet,anctus e",
                "msg_type": "q",
                "media_files": []
            },
            "category": 1,
            "client": 2
        }

    def test_make_requery(self):
        send = self.client.post(
            reverse('queries'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        data={
            "message": {
            "message": "reconsulta",
            "msg_type": "r",
            "media_files": []
            }
        }
        # print(send)
        query = Query.objects.get(pk=send.data["id"])
        query.status = 4
        query.save()
        self.assertEqual(int(Query.objects.get(pk=send.data["id"]).status), 4)
        response = self.client.put(
            reverse('query-detail', kwargs={'pk': send.data["id"]}),
            data, format='json'
        )
        self.assertEqual(int(response.data["status"]), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # import pdb; pdb.set_trace()
