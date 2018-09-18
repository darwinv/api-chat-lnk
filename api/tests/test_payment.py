"""Pruebas unitarias para el CRUD de clientes."""
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
import json
from ..models import SellerContact, MonthlyFee, User, Sale, QueryPlansAcquired
from rest_framework import status

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')


class MakePaymentNoFee(APITestCase):
    """Prueba de Crear Pagos."""

    fixtures = ['data', 'data2', 'data3', 'test_payment']

    def setUp(self):
        """SetUp."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        self.valid_payload = {
            "amount": 300,
            "operation_number": "123123-ERT",
            "observations": "opcional",
            "monthly_fee": 1,
            "payment_type": 2,
            "bank": 1
        }

    def test_less_amount(self):
        """Monto del pago menor a la cuota correspondiente."""
        data = self.valid_payload.copy()
        data["amount"] = 299
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_permissions(self):
        """Permiso invalido."""
        data = self.valid_payload.copy()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer CLIENTEFEk2avXwe09l8lqS3zTc0Q3Qsl7yHY')
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_one_product_no_fee_success(self):
        """Crear pago con un producto, con una cuota exitosa."""
        data = self.valid_payload
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        mfee = MonthlyFee.objects.get(pk=data["monthly_fee"])
        user = User.objects.get(pk=5)
        contact = SellerContact.objects.get(pk=2)
        q_acqd = QueryPlansAcquired.objects.get(pk=1)
        sale = Sale.objects.get(pk=1)
        # compruebo si el tipo de contacto paso a 3
        self.assertEqual(3, contact.type_contact)
        # compruebo el estado de la cuota a  2
        self.assertEqual(2, mfee.status)
        # compruebo el cambio de  codigo
        self.assertEqual(user.code, 'C20521663147')
        # estado de la  venta debe estar pagado
        self.assertEqual(sale.status, 3)
        # estado de la adquirida por pagar
        self.assertEqual(q_acqd.queries_to_pay, 0)
        # disponibles
        self.assertEqual(q_acqd.available_queries, 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_two_product_no_fee_success(self):
        """Crear pago con 2 productos, con una cuota (contado) exitosa."""
        data = {
            "amount": 1200,
            "operation_number": "123423-ERT",
            "observations": "opcional",
            "monthly_fee": 2,
            "payment_type": 2,
            "bank": 1
        }
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        mfee = MonthlyFee.objects.get(pk=data["monthly_fee"])
        user = User.objects.get(pk=5)
        contact = SellerContact.objects.get(pk=2)
        q_acqd = QueryPlansAcquired.objects.get(pk=2)
        q_acqd_2 = QueryPlansAcquired.objects.get(pk=3)
        sale = Sale.objects.get(pk=2)
        # compruebo si el tipo de contacto paso a 3
        self.assertEqual(3, contact.type_contact)
        # compruebo el estado de la cuota a  2
        self.assertEqual(2, mfee.status)
        # compruebo el cambio de  codigo
        self.assertEqual(user.code, 'C20521663147')
        # estado de la  venta debe estar pagado
        self.assertEqual(sale.status, 3)
        # estado de la adquirida por pagar
        self.assertEqual(q_acqd.queries_to_pay, 0)
        # disponibles
        self.assertEqual(q_acqd.available_queries, 2)
        self.assertEqual(q_acqd_2.available_queries, 6)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_no_monthly_fee(self):
    #     """cuota mensual no existe."""
    #     data = self.valid_payload.copy()
    #     del data["monthly_fee"]
    #     response = self.client.post(
    #         reverse('payment'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_optional_observations(self):
    #     """Observaciones son opcionales."""
    #     data = self.valid_payload.copy()
    #     del data["observations"]
    #     response = self.client.post(
    #         reverse('payment'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_invalid_monthly_fee(self):
    #     """cuota mensual no existe."""
    #     data = self.valid_payload.copy()
    #     data["monthly_fee"] = 2
    #     response = self.client.post(
    #         reverse('payment'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_no_operation_number(self):
    #     """No envia numero de operacion."""
    #     data = self.valid_payload.copy()
    #     del data["operation_number"]
    #     response = self.client.post(
    #         reverse('payment'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_no_amount(self):
    #     """No envia numero de operacion."""
    #     data = self.valid_payload.copy()
    #     del data["amount"]
    #     response = self.client.post(
    #         reverse('payment'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class MakePaymentWithFee(APITestCase):
    """Prueba de Crear Pagos."""

    fixtures = ['data', 'data2', 'data3', 'test_payment2']

    def setUp(self):
        """SetUp."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer EGsnU4Cz3Mx50UCuLrc20mup10s0Gz')
        self.valid_payload = {
            "amount": 450,
            "operation_number": "123123-ERT",
            "observations": "opcional",
            "monthly_fee": 2,
            "payment_type": 2,
            "bank": 1
        }

    def test_one_product_fee_success(self):
        """Crear pago con un producto, con una cuota exitosa."""
        data = self.valid_payload
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        mfee = MonthlyFee.objects.get(pk=data["monthly_fee"])
        user = User.objects.get(pk=5)
        contact = SellerContact.objects.get(pk=2)
        q_acqd = QueryPlansAcquired.objects.get(pk=1)
        sale = Sale.objects.get(pk=2)
        # compruebo si el tipo de contacto paso a 3
        self.assertEqual(3, contact.type_contact)
        # compruebo el estado de la cuota a  2
        self.assertEqual(2, mfee.status)
        # compruebo el cambio de  codigo
        self.assertEqual(user.code, 'C20521663147')
        # estado de la  venta debe estar en progreso
        self.assertEqual(sale.status, 2)
        # estado de la adquirida por pagar
        self.assertEqual(q_acqd.queries_to_pay, 3)
        # disponibles
        self.assertEqual(q_acqd.available_queries, 3)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_two_product_fee_success(self):
        """Crear pago con 2 productos producto, en 2 cuotas exitosa."""
        data = {
            "amount": 800,
            "operation_number": "123123-ERT",
            "observations": "opcional",
            "monthly_fee": 4,
            "payment_type": 2,
            "bank": 1
        }
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        mfee = MonthlyFee.objects.get(pk=data["monthly_fee"])
        user = User.objects.get(pk=5)
        contact = SellerContact.objects.get(pk=2)
        q_acqd = QueryPlansAcquired.objects.get(pk=3)
        q_acqd_2 = QueryPlansAcquired.objects.get(pk=2)
        sale = Sale.objects.get(pk=3)
        # compruebo si el tipo de contacto paso a 3
        self.assertEqual(3, contact.type_contact)
        # compruebo el estado de la cuota a  2
        self.assertEqual(2, mfee.status)
        # compruebo el cambio de  codigo
        self.assertEqual(user.code, 'C20521663147')
        # estado de la  venta debe estar en progreso
        self.assertEqual(sale.status, 2)
        # estado de la adquirida por pagar
        self.assertEqual(q_acqd.queries_to_pay, 8)
        # disponibles
        self.assertEqual(q_acqd.available_queries, 4)
        # cambio
        self.assertEqual(q_acqd_2.queries_to_pay, 3)
        # disponibles
        self.assertEqual(q_acqd_2.available_queries, 3)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_two_product_fee_success_2nd_payment(self):
        """Crear pago 2da cuota, de 2 productos, en 2 cuotas exitosa."""
        data = {
            "amount": 800,
            "operation_number": "123123-ERT",
            "observations": "opcional",
            "monthly_fee": 4,
            "payment_type": 2,
            "bank": 1
        }
        data2 = {
            "amount": 800,
            "operation_number": "123124-ERT",
            "observations": "opcional",
            "monthly_fee": 5,
            "payment_type": 2,
            "bank": 1
        }
        response = self.client.post(
            reverse('payment'),
            data=json.dumps(data),
            content_type='application/json'
        )
        response2 = self.client.post(
            reverse('payment'),
            data=json.dumps(data2),
            content_type='application/json'
        )
        mfee = MonthlyFee.objects.get(pk=data["monthly_fee"])
        mfee2 = MonthlyFee.objects.get(pk=data2["monthly_fee"])
        user = User.objects.get(pk=5)
        contact = SellerContact.objects.get(pk=2)
        q_acqd = QueryPlansAcquired.objects.get(pk=3)
        q_acqd_2 = QueryPlansAcquired.objects.get(pk=2)
        sale = Sale.objects.get(pk=3)
        # compruebo si el tipo de contacto paso a 3
        self.assertEqual(3, contact.type_contact)
        # compruebo el estado de la cuota a  2
        self.assertEqual(2, mfee.status)
        self.assertEqual(2, mfee2.status)
        # compruebo el cambio de  codigo
        self.assertEqual(user.code, 'C20521663147')
        # estado de la  venta debe estar en progreso
        self.assertEqual(sale.status, 2)
        # estado de la adquirida por pagar
        self.assertEqual(q_acqd.queries_to_pay, 4)
        # disponibles
        self.assertEqual(q_acqd.available_queries, 8)
        # estado de la adquirida por pagar
        self.assertEqual(q_acqd_2.queries_to_pay, 0)
        # disponibles
        self.assertEqual(q_acqd_2.available_queries, 6)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)



class PaymentPendig(APITestCase):
    """Prueba de Traer Pagos Pendientes."""

    fixtures = ['data', 'data2', 'data3', 'test_payment']

    def setUp(self):
        """SetUp."""
        pass

    def test_get_payment_pending(self):
        """Crear pago."""

        response = self.client.get(
            reverse('sale-payment-pending'),
            {'document_number': '24612582'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetFeePaymentPendig(APITestCase):
    """Prueba de Traer Pagos Pendientes."""

    fixtures = ['data', 'data2', 'data3', 'test_payment']

    def setUp(self):
        """SetUp."""
        pass

    def test_get_payment_pending(self):
        """Crear pago."""

        response = client.get(
            reverse('fee-payment-pending-detail', kwargs={'pk': 1}),
             format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetContactsEfectiveSale(APITestCase):
    """Devolver data de contactos."""

    fixtures = ['data', 'data2', 'data3', 'test_contact']

    def setUp(self):
        """Setup."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer RCOM8gcbsOv56QFlcCJpgDENETGCLr')

    def test_get_contact_sale(self):
        """Devolver Ventas Contacto."""
        data = {"email": "ccccc@mail.com"}
        response = self.client.get(reverse('payment-pending-by-client-detail'), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
