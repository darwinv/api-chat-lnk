from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import Seller
from rest_framework import status
from api.serializers.actors import SellerSerializer
import pdb

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer zfMCmzJkLJGkVOwtQipByVSTkXOVEb')


class GetAllSellers(APITestCase):
    """ Test module for GET all sellers API """

    def setUp(self):
        pass

    def test_get_all_sellers(self):
        # get API response
        response = client.get(reverse('sellers'))
        # get data from db
        sellers = Seller.objects.all()
        serializer = SellerSerializer(sellers, many=True)
        print(response.data['results'])
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
