from django.db import models
from django.contrib.auth.models import AbstractUser
from api.api_choices_models import ChoicesAPI as Ch


class Countries(models.Model):
    name = models.CharField(max_length=90, unique=True)
    code_phone = models.CharField(max_length=4)
    iso_code = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return self.name


class Ciiu(models.Model):
    code = models.CharField(max_length=4, unique=True)
    description = models.CharField(max_length=255)


class Department(models.Model):
    name = models.CharField(max_length=55)

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(max_length=55)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=55)
    province = models.ForeignKey(Province, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Address(models.Model):
    street = models.CharField(max_length=155, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True)
    province = models.ForeignKey(Province, on_delete=models.PROTECT, null=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT, null=True)


class Zone(models.Model):
    name = models.CharField(max_length=45)
    districts = models.ManyToManyField(District, db_table='zones_districts')

    def __str__(self):
        return self.name


class Permmission(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=220)
    code = models.CharField(max_length=12)


# La Clase Rol difiere el funcionamiento de grupo
# por eso creamos un modelo nuevo

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    permissions = models.ManyToManyField(Permmission, db_table='role_permission')

    def __str__(self):
        return self.name


# Utilizaremos el metodo de Heredar de AbstractUser
# para personalizar el modelo de usuarios
class User(AbstractUser):
    """Modelo de Usuario hereda de AbstractUser."""

    #  class Meta:
    #      db_table = 'user'
    first_name = models.CharField(max_length=30, blank=True)
    nick = models.CharField(max_length=45, blank=True)
    email_exact = models.CharField(max_length=150, unique=True)
    telephone = models.CharField(max_length=14, blank=True, null=True)
    cellphone = models.CharField(max_length=14, blank=True, null=True)
    photo = models.CharField(max_length=250, null=True)
    document_type = models.CharField(max_length=1, choices=Ch.user_document_type)
    document_number = models.CharField(max_length=45, unique=True)
    img_document_number = models.CharField(max_length=250, null=True)
    ruc = models.CharField(max_length=40, unique=True, null=True, blank=True)
    code = models.CharField(max_length=45, unique=True)
    anonymous = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    nationality = models.ForeignKey(Countries, on_delete=models.PROTECT, default=1)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, default=1)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True)
    residence_country = models.ForeignKey(Countries, on_delete=models.PROTECT, null=True, related_name="residence")
    foreign_address = models.CharField(max_length=100, blank=True, null=True)
    key = models.CharField(max_length=90, blank=True, null=True)


# Aplicamos herencia multi tabla para que
# Seller herede de User y se vincule 1 a 1

class Seller(User):
    """Modelo de Vendedor (hereda de User)."""

    cv = models.CharField(max_length=100, null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, null=True)
    ciiu = models.CharField(max_length=4, null=True)

    class Meta:
        """Meta."""

        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'


class Objection(models.Model):
    name = models.CharField(max_length=65)

    def __str__(self):
        return self.name


class SellerContactNoEfective(models.Model):
    """Contacto No Efectivo."""

    firstname = models.CharField(max_length=45, null=True)
    lastname = models.CharField(max_length=55, null=True)
    type_contact = models.CharField(max_length=1, choices=Ch.client_type_client)  # si es efectivo o no efectivo
    document_type = models.CharField(max_length=1, choices=Ch.user_document_type)
    document_number = models.CharField(max_length=45)
    email = models.CharField(max_length=150)
    civil_state = models.CharField(max_length=1, choices=Ch.client_civil_state, null=True)
    birthdate = models.DateField()
    contact_bussinessname = models.CharField(max_length=45, null=True)
    agent_firstname = models.CharField(max_length=45, null=True)
    agent_lastname = models.CharField(max_length=45, null=True)
    latitude = models.CharField(max_length=45)
    longitude = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT)
    objection = models.ForeignKey(Objection, on_delete=models.PROTECT)

    def __str__(self):
        return self.contact_firstname


class EconomicSector(models.Model):
    name = models.CharField(max_length=45)

    def __str__(self):
        return self.name


class LevelInstruction(models.Model):
    name = models.CharField(max_length=45)

    def __str__(self):
        return self.name


class Client(User):
    """Modelo de Cliente (herede de usuario)."""

    type_client = models.CharField(max_length=1, choices=Ch.client_type_client)
    sex = models.CharField(max_length=1, choices=Ch.client_sex, blank=True)
    commercial_reason = models.CharField(max_length=45, null=True)
    civil_state = models.CharField(max_length=1, choices=Ch.client_civil_state, null=True)
    birthdate = models.DateField(null=True)
    ciiu = models.CharField(max_length=4, blank=True)
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


class Category(models.Model):
    name = models.CharField(max_length=45, unique=True)
    image = models.CharField(max_length=169)
    description = models.CharField(max_length=255)
    payment_per_answer = models.FloatField()

    def __str__(self):
        return self.name


class Specialist(User):
    """Modelo de Especialista (herede de user)."""

    business_name = models.CharField(max_length=55)
    type_specialist = models.CharField(max_length=1, choices=Ch.specialist_type_specialist)
    star_rating = models.IntegerField(null=True)
    cv = models.CharField(max_length=150, null=True)
    payment_per_answer = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    class Meta:
        """Meta datos."""

        verbose_name = 'Specialist'
        verbose_name_plural = 'Specialists'


class SpecialistContract(models.Model):
    name_case = models.CharField(max_length=100)

    state = models.CharField(max_length=1, choices=Ch.specialistcontract_state)
    declined_motive = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    specialist = models.ForeignKey(Specialist, on_delete=models.PROTECT)

    def __str__(self):
        return self.name_case


class ContractCategory(models.Model):
    url_file = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.category


class Promotion(models.Model):
    code = models.CharField(max_length=45)
    discount = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()

    type_discount = models.CharField(max_length=1, choices=Ch.promotions_type)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class Plan(models.Model):
    name = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=45)
    query_amount = models.IntegerField()
    expiration_number = models.PositiveIntegerField()
    price = models.FloatField()
    is_active = models.BooleanField()
    is_billable = models.BooleanField()
    created_at = models.DateTimeField()
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    seller = models.ManyToManyField(Seller, through='ProductsSellerNoBillable')

    def __str__(self):
        return self.name


class Purchase(models.Model):
    code = models.PositiveIntegerField()
    total_amount = models.FloatField()
    reference_number = models.CharField(max_length=30)
    fee_number = models.PositiveIntegerField()
    latitude = models.CharField(max_length=45, null=True)
    longitude = models.CharField(max_length=45, null=True)
    query_amount = models.PositiveIntegerField()
    query_available = models.PositiveIntegerField()
    is_promotional = models.BooleanField()
    last_number_fee_paid = models.PositiveIntegerField()

    status = models.CharField(max_length=1, choices=Ch.purchase_status)
    expiration_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.PROTECT, null=True, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT, null=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return self.reference_number


class ProductsSellerNoBillable(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT)
    query_amount_no_billable = models.IntegerField()
    query_amount_no_billable_available = models.IntegerField()
    date = models.DateField(unique=True)


class PaymentType(models.Model):
    name = models.CharField(max_length=45)

    def __str__(self):
        return self.name


class Fee(models.Model):
    reference_number = models.CharField(max_length=20)
    fee_order_number = models.PositiveIntegerField()  # El numero de cuota que se esta pagando
    fee_amount = models.FloatField()  # total pagado para esta cuota
    transaction_code = models.CharField(max_length=45)

    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.PROTECT)
    api_client = models.TextField(null=True)
    tablename = models.CharField(max_length=17, null=True)

    status = models.CharField(max_length=1, choices=Ch.fee_status)
    date = models.DateField()
    datetime_payment = models.DateTimeField(null=True)

    def __str__(self):
        return self.reference_number


class CreditCard(models.Model):
    number_card = models.CharField(max_length=16)
    cvc = models.CharField(max_length=4)
    expiration_date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.PROTECT)


class CulqiPayment(models.Model):
    culqi_code = models.CharField(max_length=40)

    status = models.CharField(max_length=1, choices=Ch.culqipayment_status)
    credit_cartd = models.ForeignKey(CreditCard, on_delete=models.PROTECT)


# Cuando se reconsulta pasa a Requested Derived y se asigna
# al especialista que respondio previamente,
# la reconsulta tiene precedente y no se descuenta del plan

class Query(models.Model):
    title = models.CharField(max_length=50)

    status = models.CharField(max_length=1, choices=Ch.query_status)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    calification = models.PositiveSmallIntegerField(null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    specialist = models.ForeignKey(Specialist, on_delete=models.PROTECT)

    def __str__(self):
        return self.title


# Motivos de declinar la consulta
class DeclinedMotive(models.Model):
    motive = models.CharField(max_length=255)
    query_id = models.ForeignKey(Query, on_delete=models.PROTECT)
    specialist_id = models.ForeignKey(Specialist, on_delete=models.PROTECT)


class QueryLog(Query):
    actions = models.CharField(max_length=10)
    changed_on = models.DateTimeField()


class Message(models.Model):
    message = models.TextField()

    msg_type = models.CharField(max_length=1, choices=Ch.message_msg_type)
    created_at = models.DateTimeField(auto_now_add=True)
    specialist = models.ForeignKey(Specialist, on_delete=models.PROTECT)
    query = models.ForeignKey(Query, on_delete=models.PROTECT)

    def __str__(self):
        return self.message


class MessageFile(models.Model):
    url = models.CharField(max_length=100)

    type_file = models.CharField(max_length=1, choices=Ch.messagefile_type_file)
    message = models.ForeignKey(Message, on_delete=models.PROTECT)


class Interval(models.Model):
    interval = models.IntegerField()

    def __str__(self):
        return str(self.interval)


class AlertCategory(models.Model):
    name = models.CharField(max_length=1, choices=Ch.alertcategory_name)
    interval = models.ForeignKey(Interval, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Alert(models.Model):
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    category = models.ForeignKey(AlertCategory, on_delete=models.PROTECT)
    role = models.ManyToManyField(Role, db_table='role_alert')

    def __str__(self):
        return self.title


class FeeNextMonthSeller(models.Model):
    fee_promotion = models.PositiveIntegerField()
    fee_contacts = models.PositiveIntegerField()
    fee_products = models.PositiveIntegerField()


class TransactionCode(models.Model):
    code = models.CharField(max_length=50)
    short_description = models.CharField(max_length=25)
    long_description = models.CharField(max_length=250)


class Quota(models.Model):
    value = models.PositiveIntegerField()
    count_contacts = models.PositiveIntegerField(null=True)
    date = models.DateField(unique=True)


# Ingresar en parametros number_requery
# language
# tax
# email_support
# time_delay_response
# seller_available_promotional
# time_to_answer
class Parameter(models.Model):
    parameter = models.CharField(max_length=45)
    value = models.CharField(max_length=50)

    def __str__(self):
        return "Parametro: " + self.parameter
