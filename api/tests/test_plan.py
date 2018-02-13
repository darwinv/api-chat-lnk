"""Test para Planes."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.utils.tools import get_date_by_time 
from api.models import QueryPlansAcquired

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx5bUCuLrc2hmup51sSGz')

class GetPlanByPIN(APITestCase):
    """Test module for GET plan deactive API."""

    fixtures = ['data', 'data2', 'data3', 'test_plan']

    def setUp(self):
        # Token de un cliente con plan activo
        client.credentials(HTTP_AUTHORIZATION='Bearer kEphPGlavEforKavpDzuZSgK0zpoXS')

    def test_get_plan_by_pin(self):

        """Setup."""
        self.valid_payload = {
            "plan_name": "Minipack",
            "query_quantity": 6,
            "available_queries": 6,
            "validity_months": 3,
            "expiration_date": "2018-05-14",
            "price": "700.00",
            "is_active": False
        }

        # get API response        
        response = client.get(reverse('activation-plan', args=('INTEL12345',)))
        
        self.assertEqual(response.data, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_plan_active(self):
        """Traer plan activo para activacion, FALSO
        no se pueden activar un plan activado"""
        """Setup."""
        self.valid_payload = {
            "plan_name": "Minipack",
            "query_quantity": 6,
            "available_queries": 6,
            "validity_months": 3,
            "expiration_date": "2018-05-14",
            "price": "700.00",
            "is_active": True
        }

        # get API response        
        response = client.get(reverse('activation-plan', args=('INTEL12345',)))
        
        self.assertNotEqual(response.data, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UpdatePlanActiveByAPI(APITestCase):
    """Test module for Activate Plan by API API."""

    fixtures = ['data', 'data2', 'data3', 'test_plan']

    def setUp(self):
        # Token de un cliente con plan activo
        client.credentials(HTTP_AUTHORIZATION='Bearer kEphPGlavEforKavpDzuZSgK0zpoXS')

    def test_get_plan_by_pin(self):

        """Setup."""
        code = 'INTEL12345'

        plan_adquired = QueryPlansAcquired.objects.values('validity_months')\
            .filter(sale_detail__pin_code=code, is_active = False)[:1].get()
        
        expiration_date = get_date_by_time(plan_adquired['validity_months'])

        self.valid_payload = {
            "expiration_date": expiration_date.strftime('%Y-%m-%d'),
            "is_active": True
        }

        # get API response
        response = client.put(reverse('activation-plan', args=(code,)))
        
        self.assertEqual(response.data, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

