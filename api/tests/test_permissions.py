from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import User
from rest_framework import status
from api.serializers.category import CategorySerializer

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')

class GetUsers(APITestCase):
    fixtures = ['data','data2','data3']
    def setUp(self):
        self.url = '/users/'
    def test_get_users(self):
        # get API response

        response = client.get(self.url,content_type='application/json')
        
        # get data from db
        user = User.objects.all()
        # self.assertEqual(response.data, "ey")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
