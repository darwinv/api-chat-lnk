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
