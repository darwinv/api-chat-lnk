"""Modelos de la Api."""

from django.db import models
from django.contrib.auth.models import AbstractUser
from api.api_choices_models import ChoicesAPI as Ch
from django.utils.translation import ugettext_lazy as _

class Countries(models.Model):
    """Paises."""

    name = models.CharField(max_length=90, unique=True)
    code_phone = models.CharField(max_length=4)
    iso_code = models.CharField(max_length=4, unique=True)

    def __str__(self):
        """nombre."""
        return self.name


class Ciiu(models.Model):
    """Codigo CIIU."""

    code = models.CharField(max_length=4, unique=True)
    description = models.CharField(max_length=255)


class Department(models.Model):
    """Departamento."""

    name = models.CharField(max_length=55)

    def __str__(self):
        """nombre."""
        return self.name


class Province(models.Model):
    """Provincia."""

    name = models.CharField(max_length=55)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    def __str__(self):
        """Nombre."""
        return self.name


class District(models.Model):
    """Distrito."""

    name = models.CharField(max_length=55)
    province = models.ForeignKey(Province, on_delete=models.PROTECT)

    def __str__(self):
        """Nombre."""
        return self.name


class Address(models.Model):
    """Direccion."""

    street = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True)
    province = models.ForeignKey(Province, on_delete=models.PROTECT, null=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT, null=True)


class Zone(models.Model):
    """Zona."""

    name = models.CharField(max_length=45)
    districts = models.ManyToManyField(District, db_table='zones_districts')

    def __str__(self):
        """Nombre."""
        return self.name


class Permmission(models.Model):
    """Permisos."""

    name = models.CharField(max_length=150)
    description = models.CharField(max_length=220)
    code = models.CharField(max_length=12)


# La Clase Rol difiere el funcionamiento de grupo
# por eso creamos un modelo nuevo

class Role(models.Model):
    """Rol."""

    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    permissions = models.ManyToManyField(
        Permmission, db_table='role_permission')

    def __str__(self):
        """Nombre del Rol."""
        return self.name


# Utilizaremos el metodo de Heredar de AbstractUser
# para personalizar el modelo de usuarios
class User(AbstractUser):
    """Modelo de Usuario hereda de AbstractUser."""

    #  class Meta:
    #      db_table = 'user'
    nick = models.CharField(_('nick'), max_length=45, blank=True)
    email_exact = models.CharField(_('email'), max_length=150, unique=True)
    telephone = models.CharField(_('phone'), max_length=14,
                                 blank=True, null=True)
    cellphone = models.CharField(_('cellphone'), max_length=14,
                                 blank=True, null=True)
    code_telephone = models.ForeignKey(Countries, null=True,
                                       on_delete=models.PROTECT,
                                       related_name="prefix_telephone")
    code_cellphone = models.ForeignKey(Countries, null=True,
                                       on_delete=models.PROTECT,
                                       related_name="prefix_cellphone")
    photo = models.CharField(_('photo'), max_length=250, null=True)
    document_type = models.CharField(_('type document'), max_length=1,
                                     choices=Ch.user_document_type)
    document_number = models.CharField(_('document number'), max_length=45)
    img_document_number = models.CharField(_('upload document'),
                                           max_length=250, null=True)
    ruc = models.CharField(max_length=40, null=True, blank=True)
    code = models.CharField(_('code'), max_length=45)
    anonymous = models.BooleanField(_('anonymous'), default=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now_add=True)
    nationality = models.ForeignKey(Countries, default=1,
                                    on_delete=models.PROTECT,
                                    verbose_name=_('nationality'))
    role = models.ForeignKey(Role, default=1,
                             on_delete=models.PROTECT,
                             verbose_name=_('role'))
    address = models.ForeignKey(Address, null=True,
                                on_delete=models.PROTECT,
                                verbose_name=_('address'))
    residence_country = models.ForeignKey(Countries, null=True,
                                          on_delete=models.PROTECT,
                                          related_name="residence",
                                          verbose_name=_('residence country'))
    foreign_address = models.CharField(_('foreign address'), max_length=200,
                                       blank=True, null=True)
    key = models.CharField(max_length=90, blank=True, null=True)
    status = models.CharField(max_length=1, choices=Ch.user_status,
                              default='0')


# Aplicamos herencia multi tabla para que
# Seller herede de User y se vincule 1 a 1


class Seller(User):
    """Modelo de Vendedor (hereda de User)."""

    cv = models.CharField(max_length=100, null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, null=True)
    ciiu = models.ForeignKey(Ciiu, null=True, blank=True)

    class Meta:
        """Meta."""

        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'


class Objection(models.Model):
    """Objecion."""

    name = models.CharField(max_length=65)

    def __str__(self):
        """Nombre."""
        return self.name


class EconomicSector(models.Model):
    """Sector Economico."""

    name = models.CharField(max_length=45)

    def __str__(self):
        """Nombre."""
        return self.name


class LevelInstruction(models.Model):
    """Nivel de Instruccion."""

    name = models.CharField(max_length=45)

    def __str__(self):
        """Representacion en String."""
        return self.name


class SellerContactNoEfective(models.Model):
    """Contacto No Efectivo."""

    first_name = models.CharField(max_length=45, null=True)
    last_name = models.CharField(max_length=55, null=True)
    type_contact = models.CharField(max_length=1, choices=Ch.client_type_client)  # si es efectivo o no efectivo
    document_type = models.CharField(max_length=1, choices=Ch.user_document_type)
    document_number = models.CharField(max_length=45)
    email = models.CharField(max_length=150, null=True)
    civil_state = models.CharField(max_length=1, choices=Ch.client_civil_state, null=True)
    birthdate = models.DateField(null=True)
    institute = models.CharField(max_length=100, null=True, blank=True)
    ciiu = models.ForeignKey(Ciiu, null=True)
    activity_description = models.CharField(max_length=255, null=True, blank=True)
    photo = models.CharField(max_length=250, null=True)
    about = models.CharField(max_length=255, null=True, blank=True)
    cellphone = models.CharField(max_length=14, blank=True, null=True)
    telephone = models.CharField(max_length=14, blank=True, null=True)
    ocupation = models.CharField(max_length=1, choices=Ch.client_ocupation, blank=True)
    profession = models.CharField(max_length=45, null=True)
    business_name = models.CharField(max_length=45, null=True)
    commercial_reason = models.CharField(max_length=45, null=True)
    agent_firstname = models.CharField(max_length=45, null=True)
    agent_lastname = models.CharField(max_length=45, null=True)
    sex = models.CharField(max_length=1, choices=Ch.client_sex, blank=True)
    latitude = models.CharField(max_length=45, blank=True)
    longitude = models.CharField(max_length=45, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.CharField(max_length=45, null=True)
    ruc = models.CharField(max_length=40, null=True, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT)
    economic_sector = models.ForeignKey(EconomicSector, on_delete=models.PROTECT, null=True)
    objection = models.ForeignKey(Objection, on_delete=models.PROTECT)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True)
    level_instruction = models.ForeignKey(LevelInstruction, on_delete=models.PROTECT, null=True)
    nationality = models.ForeignKey(Countries, on_delete=models.PROTECT, default=1)

    def __str__(self):
        """Nombre del Contacto."""
        return self.first_name


class Client(User):
    """Modelo de Cliente (herede de usuario)."""

    type_client = models.CharField(max_length=1, choices=Ch.client_type_client)
    sex = models.CharField(max_length=1, choices=Ch.client_sex, blank=True)
    commercial_reason = models.CharField(max_length=45, null=True)
    civil_state = models.CharField(max_length=1, choices=Ch.client_civil_state, null=True)
    birthdate = models.DateField(null=True)
    # ciiu = models.CharField(max_length=4, blank=True)
    ciiu = models.ForeignKey(Ciiu, null=True)
    activity_description = models.CharField(max_length=255, null=True, blank=True)
    institute = models.CharField(max_length=100, null=True, blank=True)
    ocupation = models.CharField(max_length=1, choices=Ch.client_ocupation)
    about = models.CharField(max_length=255, null=True, blank=True)
    business_name = models.CharField(max_length=45, null=True)
    agent_firstname = models.CharField(max_length=45, null=True)
    agent_lastname = models.CharField(max_length=45, null=True)
    position = models.CharField(max_length=45, null=True)
    profession = models.CharField(max_length=45, null=True)
    economic_sector = models.ForeignKey(EconomicSector, on_delete=models.PROTECT, null=True)
    level_instruction = models.ForeignKey(LevelInstruction, on_delete=models.PROTECT, null=True)
    seller_asigned = models.ForeignKey(Seller, on_delete=models.PROTECT, null=True)

    class Meta:
        """Modelo de Cliente."""

        verbose_name = 'Client'
        verbose_name_plural = 'Clients'


class ContractType(models.Model):
    """Contratos Categorias."""

    name = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)


class Contract(models.Model):
    """Contratos Historico."""

    url_file = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=False)
    validity_months = models.PositiveIntegerField()
    expiration_date = models.DateField()
    type_contract = models.ForeignKey(ContractType, on_delete=models.PROTECT)


class Category(models.Model):
    """Especialidad."""

    name = models.CharField(max_length=45, unique=True)
    image = models.CharField(max_length=169)
    description = models.CharField(max_length=255)
    # payment_per_answer = models.DecimalField(max_digits=10, decimal_places=2)
    fixed_commission = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    variable_commission = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT, null=True)

    def __str__(self):
        """Repr."""
        return self.name


class Bank(models.Model):
    """Bancos del Peru."""

    name = models.CharField(_('Bank'), max_length=200)
    code = models.CharField(max_length=10)

    def __str__(self):
        """Representacion String."""
        return self.name


class Specialist(User):
    """Modelo de Especialista (herede de user)."""

    business_name = models.CharField(max_length=55)
    type_specialist = models.CharField(max_length=1, choices=Ch.specialist_type_specialist)
    star_rating = models.IntegerField(null=True)
    cv = models.CharField(max_length=150, null=True)
    payment_per_answer = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    class Meta:
        """Meta datos."""

        verbose_name = 'Specialist'
        verbose_name_plural = 'Specialists'


class Clasification(models.Model):
    """Clasificacion para planes de consulta."""

    name = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String."""
        return self.name


class ProductType(models.Model):
    """Tipo de Producto."""

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String."""
        return self.name


class QueryPlans(models.Model):
    """Planes de Consultas (Producto)."""

    name = models.CharField(max_length=50)
    query_quantity = models.IntegerField()
    validity_months = models.PositiveIntegerField()
    maximum_response_time = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT)
    clasification = models.ForeignKey(Clasification, on_delete=models.PROTECT)
    non_billable = models.ManyToManyField(Seller, through='SellerNonBillablePlans')

    def __str__(self):
        """String."""
        return self.name


class SellerNonBillablePlans(models.Model):
    """Planes no Facturables Asignados a Vendedores."""

    seller = models.ForeignKey(Seller, on_delete=models.PROTECT)
    query_plans = models.ForeignKey(QueryPlans, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    number_month = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Match(models.Model):
    """Contratacion de Especialista (Producto)."""

    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT)
    speciality = models.ForeignKey(Category, on_delete=models.PROTECT)


class Sale(models.Model):
    """Venta."""

    created_at = models.DateTimeField(auto_now_add=True)
    place = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_number = models.CharField(max_length=20)
    description = models.TextField()
    is_fee = models.BooleanField(default=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    seller = models.ForeignKey(Seller, null=True, on_delete=models.PROTECT)
    # status = models.IntegerField()


class SaleDetail(models.Model):
    """Detalle de Venta."""

    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    pin_code = models.CharField(max_length=50)
    is_billable = models.BooleanField(default=True)
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT, null=True)
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT)
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT)


class QueryPlansAcquired(models.Model):
    """Planes de Consultas (Adquirido)."""

    expiration_date = models.DateField(null=True)
    validity_months = models.PositiveIntegerField()
    available_queries = models.PositiveIntegerField()
    query_quantity = models.PositiveIntegerField()
    activation_date = models.DateField(null=True)
    is_active = models.BooleanField(default=False)
    is_chosen = models.BooleanField(default=False)
    available_requeries = models.PositiveIntegerField()
    maximum_response_time = models.PositiveIntegerField()  # En Horas
    acquired_at = models.DateTimeField(auto_now_add=True)
    plan_name = models.CharField(max_length=50)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    query_plans = models.ForeignKey(QueryPlans, on_delete=models.PROTECT)
    sale_detail = models.ForeignKey(SaleDetail, on_delete=models.PROTECT)

    def __str__(self):
        """String."""
        return self.plan_name

class PaymentType(models.Model):
    """Tipos de Pago."""

    name = models.CharField(max_length=45)
    description = models.CharField(max_length=200, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        """Representacion String."""
        return self.name


class Payment(models.Model):
    """Pagos."""

    amount = models.FloatField()
    operation_number = models.CharField(max_length=12)
    agency_code = models.CharField(max_length=10)
    account_number_drawer = models.CharField(max_length=50)
    check_number = models.CharField(max_length=50)
    credit_cart_number = models.CharField(max_length=30)
    credit_card_cvc = models.CharField(max_length=3)
    credit_card_exp_date = models.DateField()
    authorized_by = models.ForeignKey(User, on_delete=models.PROTECT)
    authorization_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=Ch.payment_status)
    observations = models.CharField(max_length=255)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.PROTECT)


class MatchAcquired(models.Model):
    """Match Adquirido."""

    price = models.DecimalField(max_digits=10, decimal_places=2)
    cause = models.TextField()
    status = models.CharField(max_length=1, choices=Ch.match_acquired_status)
    paid_by_specialist = models.BooleanField(default=False)
    paid_by_client = models.BooleanField(default=True)
    paid_by_specialist = models.BooleanField(default=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    specialist = models.ForeignKey(Specialist, on_delete=models.PROTECT)
    sale_detail = models.ForeignKey(SaleDetail, on_delete=models.PROTECT)


class MatchAcquiredFiles(models.Model):
    """Archivos Adjuntos del Match."""

    file_url = models.CharField(max_length=100)
    type_file = models.CharField(max_length=1, choices=Ch.match_type_file)
    match_acquired = models.ForeignKey(MatchAcquired)


class MatchAcquiredLog(models.Model):
    """Log Match Adquirido."""

    changed_on = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50)
    status = models.CharField(max_length=1, choices=Ch.match_acquired_status)
    declined = models.NullBooleanField()
    declined_motive = models.CharField(max_length=255, null=True)
    match_acquired = models.ForeignKey(MatchAcquired, on_delete=models.PROTECT)


class MonthlyFee(models.Model):
    """Cuota Mensual."""

    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)  # total pagado para esta cuota
    fee_order_number = models.PositiveIntegerField()  # El numero de cuota que se esta pagando
    fee_quantity = models.PositiveIntegerField()  # numero total de cuotas
    reference_number = models.CharField(max_length=20)
    sale_detail = models.ForeignKey(SaleDetail, on_delete=models.PROTECT)
    pay_before = models.DateField()
    status = models.CharField(max_length=1, choices=Ch.fee_status)
    payment = models.ForeignKey(Payment, null=True)


class LogPaymentsCreditCard(models.Model):
    """Log Pagos Pasarela."""

    created_at = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField()
    description = models.CharField(max_length=50)
    code_api = models.CharField(max_length=100)
    # culqi


# Cuando se reconsulta pasa a Requested Derived y se asigna
# al especialista que respondio previamente,
# la reconsulta tiene precedente y no se descuenta del plan

class Query(models.Model):
    """Consultas."""

    title = models.CharField(max_length=100)
    status = models.CharField(max_length=1, choices=Ch.query_status)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    calification = models.PositiveSmallIntegerField(null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    specialist = models.ForeignKey(Specialist, on_delete=models.PROTECT, null=True)
    acquired_plan = models.ForeignKey(QueryPlansAcquired, on_delete=models.PROTECT)
    changed_on = models.DateTimeField(auto_now=True, null=True)  # Fecha en la que adjudicada la consulta

    def __str__(self):
        """Titulo."""
        return self.title


class QueryLogs(models.Model):
    """Historico de Consultas."""

    action = models.CharField(max_length=10)
    description = models.CharField(max_length=200, null=True)
    changed_on = models.DateTimeField()
    status_log = models.CharField(max_length=1, choices=Ch.query_status)
    derived = models.NullBooleanField()
    declined = models.NullBooleanField()
    declined_motive = models.TextField(null=True)
    to_specialist = models.ForeignKey(Specialist, on_delete=models.PROTECT, null=True, related_name="del_especialista")
    from_specialist = models.ForeignKey(Specialist, related_name="al_especialista", on_delete=models.PROTECT, null=True)
    query = models.ForeignKey(Query, on_delete=models.PROTECT)


# Para traerse el historico de mensajes de consultas de un especialista que ya ha respondido
# se hace la consulta de traerse todos los mensajes anteriories pertenecientes a una consulta donde ya he
# respondido
class Message(models.Model):
    """Mensaje."""

    message = models.TextField(blank=True)
    msg_type = models.CharField(max_length=1, choices=Ch.message_msg_type,
                                blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    content_type = models.CharField(max_length=1,
                                    choices=Ch.message_content_type)
    specialist = models.ForeignKey(Specialist,
                                   on_delete=models.PROTECT, null=True)
    viewed = models.BooleanField(default=False)
    file_url = models.CharField(max_length=100, blank=True)
    code = models.CharField(_('code'), max_length=45)
    room = models.CharField(max_length=200)  # Sala de chat
    query = models.ForeignKey(Query, on_delete=models.PROTECT)
    message_reference = models.ForeignKey('self', on_delete=models.PROTECT,
                                          related_name="ref", null=True)

    def __str__(self):
        """Str."""
        return self.message


#Modelo para usar con una vista existente en la base de datos
class SpecialistMessageList(models.Model):
    id = models.IntegerField(primary_key=True)
    photo = models.CharField(max_length=240, blank=True)
    nick = models.CharField(max_length=40, blank=True)
    date = models.DateField(blank=True)
    title = models.CharField(max_length=240, blank=True)
    total = models.IntegerField(blank=True)
    client = models.IntegerField(blank=True)
    specialist = models.IntegerField(blank=True)

    class Meta:
        db_table = u'specialist_message_list'
        managed = False

class FeeMonthSeller(models.Model):
    """Cuotas Mensuales del Vendedor."""

    start_month = models.DateField()  # mes de inicio de la cuota
    fee_plans = models.PositiveIntegerField()
    fee_contacts = models.PositiveIntegerField()
    complete_fee_products = models.PositiveIntegerField()
    complete_fee_contacts = models.PositiveIntegerField
    created_at = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT)


class NotificationsBack(models.Model):
    """Notificaciones del Dashboard Administrativo."""

    message = models.CharField(_('message'), max_length=255)
    viewed = models.BooleanField(_('viewed'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.PROTECT)


# Ingresar en parametros number_requery
# language
# tax
# email_support
# time_delay_response
# seller_available_promotional
# time_to_answer
# available_requeries
# medium_payment
# place_payment

class Parameter(models.Model):
    """Parametros Generales."""

    parameter = models.CharField(max_length=45)
    value = models.CharField(max_length=50)

    def __str__(self):
        """Nombre."""
        return "Parametro: " + self.parameter

""" STOREPROCEDURE y Clases exclusivas para la API"""
""" No migrar para la web"""

from api.utils.routines import get_messages_list

class SpecialistMessageList_sp(models.Model):
    id = models.IntegerField(primary_key=True)
    photo = models.CharField(max_length=240, blank=True)
    nick = models.CharField(max_length=40, blank=True)
    date = models.DateField(blank=True)
    title = models.CharField(max_length=240, blank=True)
    message = models.CharField(max_length=500,blank=True)
    client = models.IntegerField(blank=True)
    specialist = models.IntegerField(blank=True)
    total = models.IntegerField(blank=True)

    class Meta:
        managed = False

    @staticmethod
    def search(flag, user_id, aux_1, aux_2, aux_3):
        # create a cursor
        results = get_messages_list(flag, user_id, aux_1, aux_2, aux_3)
        return [SpecialistMessageList_sp(*row) for row in results]
