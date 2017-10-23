from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator

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
    street = models.CharField(max_length=155)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    province = models.ForeignKey(Province, on_delete=models.PROTECT)
    district = models.ForeignKey(District, on_delete=models.PROTECT)

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
    #  class Meta:
    #      db_table = 'user'
    nick = models.CharField(max_length=45, blank=True)
    email_exact = models.CharField(max_length=150, unique=True)
    telephone = models.CharField(max_length=14)
    cellphone = models.CharField(max_length=14)
    photo = models.CharField(max_length=250, default='preview.png', null=True)
    options_documents = (
        ('0', 'DNI'),
        ('1', 'Passport'),
        ('2', 'Foreign Card'),
    )
    document_type = models.CharField(max_length=1, choices=options_documents)
    document_number = models.CharField(max_length=45, unique=True)
    ruc = models.CharField(max_length=40, unique=True, null=True)
    code = models.CharField(max_length=45, unique=True)
    anonymous = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    nationality = models.ForeignKey(Countries, on_delete=models.PROTECT, default=1)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, default=1)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True)

# Aplicamos herencia multi tabla para que
# Seller herede de User y se vincule 1 a 1

class Seller(User):
    cv = models.CharField(max_length=100, null=True, blank=True)
    monthly_promotional_plans = models.PositiveIntegerField(null=True)
    count_month_promotional = models.PositiveIntegerField(null=True)
    count_month_plans = models.PositiveIntegerField(null=True)
    count_month_contacts = models.PositiveIntegerField(null=True)
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT)
    class Meta:
        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'


class Objection(models.Model):
    name = models.CharField(max_length=65)
    def __str__(self):
        return self.name


class SellerContactNoEfective(models.Model):
    contact_firstname = models.CharField(max_length=45, null=True)
    contact_lastname = models.CharField(max_length=55, null=True)
    options_type = (
        ('n', 'Natural'),
        ('b', 'Business'),
    )

    type_contact = models.CharField(max_length=1, choices=options_type)

    options_documents = (
        ('0', 'DNI'),
        ('1', 'Passport'),
        ('2', 'Foreign Card'),
    )
    document_type = models.CharField(max_length=1, choices=options_documents)
    document_number = models.CharField(max_length=18)
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

class Profession(models.Model):
    name = models.CharField(max_length=45)
    def __str__(self):
        return self.name

class CommercialGroup(models.Model):
    name = models.CharField(max_length=45)
    def __str__(self):
        return self.name

class EconomicSector(models.Model):
    name = models.CharField(max_length=45)
    def __str__(self):
        return self.name

class LevelInstruction(models.Model):
    name = models.CharField(max_length=45)
    def __str__(self):
        return self.name

class Client(User):
    options_type = (
        ('n', 'Natural'),
        ('b', 'Bussiness'),
    )
    type_client = models.CharField(max_length=1, choices=options_type)

    options_sex = (
        ('m', 'Male'),
        ('f', 'Female'),
    )
    sex = models.CharField(max_length=1, choices=options_sex, null=True)

    options_civil_state = (
        ('s', 'Single'),
        ('m', 'Married'),
        ('d', 'Divorce'),
        ('w', 'Widower'),
    )
    civil_state = models.CharField(max_length=1, choices=options_civil_state, null=True)
    birthdate = models.DateField(null=True)
    ciiu = models.CharField(max_length=4)
    activity_description = models.CharField(max_length=255)
    institute = models.CharField(max_length=100, null=True, blank=True)
    options_ocupation = (
        ('d', 'Dependent'),
        ('i', 'Independent'),
    )
    ocupation = models.CharField(max_length=1, choices=options_ocupation)
    about = models.CharField(max_length=255)
    business_name = models.CharField(max_length=45, null=True)
    agent_firstname = models.CharField(max_length=45, null=True)
    agent_lastname = models.CharField(max_length=45, null=True)
    position = models.CharField(max_length=45, null=True)
    profession = models.ForeignKey(Profession, on_delete=models.PROTECT, null=True)
    commercial_group = models.ForeignKey(CommercialGroup, on_delete=models.PROTECT, null=True)
    economic_sector = models.ForeignKey(EconomicSector, on_delete=models.PROTECT, null=True)
    level_instruction = models.ForeignKey(LevelInstruction, on_delete=models.PROTECT, null=True)
    seller_asigned = models.ForeignKey(Seller, on_delete=models.PROTECT, null=True)

    class Meta:
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
    business_name = models.CharField(max_length=55)
    options_type = (
        ('m', 'Main'),
        ('a', 'Associate'),
    )
    type_specialist = models.CharField(max_length=1, choices=options_type)
    star_rating = models.IntegerField(null=True)
    cv = models.CharField(max_length=150,null=True)
    payment_per_answer = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Specialist'
        verbose_name_plural = 'Specialists'

class SpecialistContract(models.Model):
    name_case = models.CharField(max_length=100)
    options_state = (
        ('r', 'Requested'),
        ('a', 'Accepted'),
        ('d', 'Declined'),
    )
    state = models.CharField(max_length=1, choices=options_state)
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
    options_type = (
        ('p', 'Percentage'),
        ('n', 'Number'),
    )
    type_discount = models.CharField(max_length=1, choices=options_type)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.code

class Plan(models.Model):
    name = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class Purchase(models.Model):
    total_amount = models.FloatField()
    reference_number = models.CharField(max_length=30)
    fee_number = models.PositiveIntegerField()
    latitude = models.CharField(max_length=45, null=True)
    longitude = models.CharField(max_length=45, null=True)
    query_available = models.PositiveIntegerField()
    is_promotional = models.BooleanField()
    last_number_fee_paid = models.PositiveIntegerField()
    option_status = (
        ('0', 'Pending'),
        ('1', 'Paid'),
    )
    status = models.CharField(max_length=1, choices=option_status)
    expiration_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.PROTECT, null=True)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT, null=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    def __str__(self):
        return self.reference_number


class Product(models.Model):
    name = models.CharField(max_length=45)
    query_amount = models.IntegerField()
    expiration_number = models.PositiveIntegerField()
    price = models.FloatField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    purchases = models.ManyToManyField(Purchase, db_table='products_purchase')
    def __str__(self):
        return self.name

class PaymentType(models.Model):
    name = models.CharField(max_length=45)
    api_client = models.TextField(null=True)
    tablename = models.CharField(max_length=17, null=True)
    def __str__(self):
        return self.name

class Fee(models.Model):
    reference_number = models.CharField(max_length=20)
    fee_order_number = models.PositiveIntegerField()
    fee_amount = models.FloatField()
    transaction_code = models.CharField(max_length=45)
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.PROTECT)
    def __str__(self):
        return self.reference_number

class CreditCard(models.Model):
    number_card = models.CharField(max_length=16)
    cvc = models.CharField(max_length=4)
    expiration_date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.PROTECT)

class CulqiPayment(models.Model):
    culqi_code = models.CharField(max_length=40)
    option_status = (
        ('w', 'Wait'),
        ('d', 'Denied'),
        ('e', 'Exhaled'),
        ('p', 'Paid'),
    )
    status = models.CharField(max_length=1, choices=option_status)
    credit_cartd = models.ForeignKey(CreditCard, on_delete=models.PROTECT)


# Cuando se reconsulta pasa a Requested Derived y se asigna
# al especialista que respondio previamente,
# la reconsulta tiene precedente y no se descuenta del plan

class Query(models.Model):
    title = models.CharField(max_length=50)
    option_status = (
        ('0', 'Requested'), # Preguntada, pendiente de derivar o responder
        ('1', 'Requested Derived'), # derivada, pendiente de declinar o responder
        ('2', 'Pending Response'), # derivada a asociado, pendiente de respuesta
        ('3', 'Pending Main Response'), # principal, pendiente de respuesta
        ('4', 'Answered Main'), # respondida por principal
        ('5', 'Answered'), # respondida por asociado
        ('6', 'Absolved Main'), # resuelta por principal
        ('7', 'Absolved'), # resuelta por asociado
    )
    status = models.CharField(max_length=1, choices=option_status)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    calification = models.PositiveSmallIntegerField()
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
    options_msg_type = (
        ('q', 'query'), # es de tipo consulta
        ('r', 'requery'), # es de tipo reconsulta
        ('a', 'answer'), # es de tipo respuesta
        )
    msg_type = models.CharField(max_length=1, choices=options_msg_type)
    created_at = models.DateTimeField(auto_now_add=True)
    specialist = models.ForeignKey(Specialist, on_delete=models.PROTECT)
    query = models.ForeignKey(Query, on_delete=models.PROTECT)

class MessageFile(models.Model):
    url = models.CharField(max_length=100)
    options_type_file = (
        ('0', 'Image'),
        ('1', 'Voice'),
        ('2', 'Document'),
    )
    type_file = models.CharField(max_length=1, choices=options_type_file)
    message = models.ForeignKey(Message, on_delete=models.PROTECT)

class Interval(models.Model):
    interval = models.IntegerField()
    def __str__(self):
        return str(self.interval)

class AlertCategory(models.Model):
    name_choices = (
        ('c', 'Critic'),
        ('m', 'Moderate'),
        ('p', 'Positive'),
    )
    name = models.CharField(max_length=1, choices=name_choices)
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
