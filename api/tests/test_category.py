from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Category
from rest_framework import status
from api.serializers.category import CategorySerializer

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')

class GetCategories(APITestCase):
    fixtures = ['data','data2']
    def setUp(self):
        pass


    def test_get_categories(self):
        # get API response
        response = client.get(reverse('categories'))
        # get data from db
        specialities = Category.objects.all()
        # serializer = CategorySerializer(specialities, many=True)
        # self.assertEqual(response.data, "ee")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
