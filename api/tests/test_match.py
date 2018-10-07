"""Pruebas unitarias para los match."""
import json
import os
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import Match

client = APIClient()
client.credentials(
    HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')  # Api Admin


class RequestMatch(APITestCase):
    """Prueba para crear un match por parte del cliente."""

    fixtures = ['data', 'data2', 'data3', 'test_match']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer HhaMCycvJ5SCLXSpEo7KerIXcNgBSt')
        self.valid_payload = {
            "category": 8,
            "subject": "Quiero demandar a la sunat",
            "file": [
                {
                    "file_url": "https://20180820-21.jpg",
                    "content_type": 1
                }
                ]
            }

    def test_no_category(self):
        """No hay especialidad."""
        data = self.valid_payload.copy()
        del data["category"]
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_category(self):
        """Especialidad no existe."""
        data = self.valid_payload.copy()
        data["category"] = 50
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_subject(self):
        """No hay especialidad."""
        data = self.valid_payload.copy()
        del data["subject"]
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_file(self):
        """No hay especialidad."""
        data = self.valid_payload.copy()
        del data["file"]
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_client_credentials(self):
        """Token no es de cliente (no autorizado)."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer FEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')
        response = self.client.post(
            reverse('queries-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_match(self):
        """Creacion Exitosa del match."""
        response = self.client.post(
            reverse('match-client'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class GetListMatch(APITestCase):
    """Devolver listado de matchs."""

    fixtures = ['data', 'data2', 'data3', 'test_match']

    def setUp(self):
        """Setup."""
        pass

    def test_get_match(self):
        """Obtener resultado 200."""
        # se provee un token de especialista el cuel tiene
        # mensajes pendientes de responders
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer HhaMCycvJ5SCLXSpEo7KerIXcNgBSt')
        response = self.client.get(reverse('match-client'),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AcceptMatchSpecialist(APITestCase):
    """Aceptar Match."""

    fixtures = ['data', 'data2', 'data3', 'test_match']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer FEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')
        self.valid_payload = {
                "payment_option_specialist": 1
            }

    def test_invalid_matchid(self):
        """Solicitud Invalida por no existir match."""
        response = self.client.put(
            reverse('match-specialist-accept', kwargs={'pk': 11}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_option_payment(self):
        """Solicitud invalida por no enviar la opcion de pago."""
        data = self.valid_payload
        del data["payment_option_specialist"]
        response = self.client.put(
            reverse('match-specialist-accept', kwargs={'pk': 2}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_option_payment(self):
        """Solicitud invalida por no enviar la opcion de pago."""
        data = self.valid_payload
        data["payment_option_specialist"] = 3
        response = self.client.put(
            reverse('match-specialist-accept', kwargs={'pk': 2}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_match_paid_bank(self):
        """Respuesta exitosa del especialista."""
        response = self.client.put(
            reverse('match-specialist-accept', kwargs={'pk': 2}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        match_status = Match.objects.get(pk=2)
        self.assertEqual(2, int(match_status.status))
        self.assertEqual(1, int(match_status.payment_option_specialist))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_permissions(self):
        """Credenciales incorrectas."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer HhaMCycvJ5SCLXSpEo7KerIXcNgBSt')
        response = self.client.put(
            reverse('match-specialist-accept', kwargs={'pk': 2}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # Permisos incorrectos
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_match_paid_discount(self):
        """Respuesta exitosa del especialista."""
        data = {
            "payment_option_specialist": 2
            }
        response = self.client.put(
            reverse('match-specialist-accept', kwargs={'pk': 2}),
            data=json.dumps(data),
            content_type='application/json'
        )
        match_status = Match.objects.get(pk=2)
        self.assertEqual(2, int(match_status.status))
        self.assertEqual(2, int(match_status.payment_option_specialist))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DeclineMatchSpecialist(APITestCase):
    """Declinar Match."""

    fixtures = ['data', 'data2', 'data3', 'test_match']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer FEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')
        self.valid_payload = {
                "declined_motive": "No poseo el tiempo para resolver un caso"
            }

    def test_invalid_matchid(self):
        """Solicitud Invalida por no existir match."""
        response = self.client.put(
            reverse('match-specialist-decline', kwargs={'pk': 11}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_permissions(self):
        """Credenciales incorrectas."""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer HhaMCycvJ5SCLXSpEo7KerIXcNgBSt')
        response = self.client.put(
            reverse('match-specialist-decline', kwargs={'pk': 2}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        # Permisos incorrectos
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_declined_motive(self):
        """Solicitud invalida por no enviar el motivo."""
        data = self.valid_payload
        del data["declined_motive"]
        response = self.client.put(
            reverse('match-specialist-decline', kwargs={'pk': 2}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_null_declined_motive(self):
        """Solicitud invalida por enviar el motivo nulo."""
        data = self.valid_payload
        data["declined_motive"] = None
        response = self.client.put(
            reverse('match-specialist-decline', kwargs={'pk': 2}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_declined_motive(self):
        """Solicitud invalida por enviar el motivo blanco."""
        data = self.valid_payload
        data["declined_motive"] = ""
        response = self.client.put(
            reverse('match-specialist-decline', kwargs={'pk': 2}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_decline_match(self):
        """Respuesta exitosa del especialista."""
        response = self.client.put(
            reverse('match-specialist-decline', kwargs={'pk': 2}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        match_status = Match.objects.get(pk=2)
        self.assertEqual(3, int(match_status.status))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetListMatchSpecialist(APITestCase):
    """Devolver listado de matchs."""

    fixtures = ['data', 'data2', 'data3', 'test_match']

    def setUp(self):
        """Setup."""
        pass

    def test_get_match(self):
        """Obtener resultado 200."""
        # se provee un token de especialista el cuel tiene
        # mensajes pendientes de responders
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer FEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')
        response = self.client.get(reverse('match-specialist'),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
