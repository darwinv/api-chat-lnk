from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Category
from rest_framework import status
from api.serializers.category import CategorySerializer

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer zfMCmzJkLJGkVOwtQipByVSTkXOVEb')

class GetCategories(APITestCase):
    def setUp(self):
        fixtures = ['data','data2']

    def test_get_categories(self):
        # get API response
        response = client.get(reverse('categories'))
        # get data from db
        specialities = Category.objects.all()
        serializer = CategorySerializer(specialities, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
