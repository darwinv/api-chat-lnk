"""Actores/Usuarios (Clientes, Especialistas, Vendedores)."""
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from api.models import User, Client, Countries
from api.models import Address, Department
from api.models import Province, District, Specialist
from api.models import Seller, Quota, Purchase, Fee
from django.utils.translation import ugettext_lazy as _
from api.api_choices_models import ChoicesAPI as c
import datetime
from django.db.models import Sum


class UserSerializer(serializers.ModelSerializer):
    """

    Serializer que unicamente va ser utilizada para.

    el servicio que devuelve todos los usuarios
    Este servicio es requerido por la web de administracion
    Unicamente expone el id y el nombre de usuario.

    """

    class Meta:

        model = User
        fields = ('id', 'username')


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('photo',)


class CommonValidation():
    def validate_img(self, photo):
        try:
            extension = photo.split(".")[1]
            valid_extensions = ['png', 'jpg', 'jpeg', 'svg']
            if not extension.lower() in valid_extensions:
                raise serializers.ValidationError(u"Unsupported image extension.")
        except Exception as e:
            raise serializers.ValidationError(u"Unsupported url of photo.")


class CustomChoiceField(serializers.ChoiceField):
    def __init__(self, choices, **kwargs):
        self.choices_to_dict = choices
        serializers.ChoiceField.__init__(self, choices, **kwargs)

    def to_representation(self, value):
        dictionary = dict(self.choices_to_dict)
        return dictionary.get(value)


class AddressSerializer(serializers.ModelSerializer):
    """

    Direccion del Serializer.

    el servicio que devuelve el ubigeo correspondiente.

    """

    department_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()

    class Meta:
        """declaracion del modelo y sus campos."""

        model = Address
        fields = ('street', 'department', 'department_name', 'province', 'province_name', 'district', 'district_name')

    def get_department_name(self, obj):
        """Devuelve departamento."""
        return str(obj.department)

    def get_province_name(self, obj):
        """Devuelve provincia."""
        return str(obj.province)

    def get_district_name(self, obj):
        """Devuelve distrito."""
        return str(obj.district)


class ClientSerializer(serializers.ModelSerializer):
    """Serializer del cliente."""

    level_instruction_name = serializers.SerializerMethodField()
    nationality_name = serializers.SerializerMethodField()
    economic_sector_name = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    profession = serializers.CharField(allow_blank=True)
    type_client = serializers.ChoiceField(choices=c.client_type_client)
    type_client_name = serializers.SerializerMethodField()
    sex = serializers.ChoiceField(choices=c.client_sex, allow_blank=True)
    sex_name = serializers.SerializerMethodField()
    document_type = serializers.ChoiceField(choices=c.user_document_type)
    document_type_name = serializers.SerializerMethodField()
    civil_state = serializers.ChoiceField(choices=c.client_civil_state, allow_blank=True)
    civil_state_name = serializers.SerializerMethodField()
    ocupation = serializers.ChoiceField(choices=c.client_ocupation, allow_blank=True)
    ocupation_name = serializers.SerializerMethodField()
    address = AddressSerializer(required=False)
    nick = serializers.CharField(required=True)
    residence_country = serializers.PrimaryKeyRelatedField(queryset=Countries.objects.all(), required=True)
    residence_country_name = serializers.SerializerMethodField()
    # last_name = serializers.CharField(required=True)
    birthdate = serializers.DateField(required=True)
    email_exact = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    photo = serializers.CharField(read_only=True)

    class Meta:
        """declaracion del modelo y sus campos."""

        model = Client
        fields = (
            'id', 'username', 'nick', 'type_client', 'type_client_name', 'first_name', 'last_name', 'password', 'photo',
            'sex', 'sex_name', 'document_type', 'document_type_name', 'document_number', 'civil_state',
            'civil_state_name', 'birthdate', 'address', 'ruc', 'email_exact', 'code', 'telephone', 'cellphone',
            'ciiu', 'activity_description', 'level_instruction', 'level_instruction_name', 'business_name',
            'agent_firstname', 'agent_lastname', 'position', 'economic_sector', 'economic_sector_name',
            'institute', 'profession', 'ocupation', 'ocupation_name', 'about', 'nationality',
            'nationality_name', "residence_country", "residence_country_name")

    def get_level_instruction_name(self, obj):
        """Devuelve nivel de instrucción."""
        return _(str(obj.level_instruction))

    def get_nationality_name(self, obj):
        """Devuelve nacionalidad del cliente."""
        return _(str(obj.nationality))

    def get_residence_country_name(self, obj):
        """Devuelve resiencia del cliente."""
        return _(str(obj.residence_country))

    def get_economic_sector_name(self, obj):
        """Devuelve sector economico (solo si es juridico)."""
        return _(str(obj.economic_sector))

    # se devuelve el valor leible y traducido
    def get_type_client_name(self, obj):
        """Devuelve tipo de cliente (Natural/Juridico)."""
        return _(obj.get_type_client_display())

    def get_sex_name(self, obj):
        """Devuelve sexo (Masculino/Femenino)."""
        return _(obj.get_sex_display())

    def get_document_type_name(self, obj):
        """Devuelve tipo de documento de identidad."""
        return _(obj.get_document_type_display())

    def get_civil_state_name(self, obj):
        """Devuelve estado civil."""
        return _(obj.get_civil_state_display())

    def get_ocupation_name(self, obj):
        """Devuelve Ocupación."""
        return _(obj.get_ocupation_display())

    def validate_natural_client(self, data):
        """Validacion para cuando es natural."""
        required = _("required")
        if 'first_name' not in data:
            raise serializers.ValidationError("first_name {}".format(required))
        if 'last_name' not in data:
            raise serializers.ValidationError("last_name {}".format(required))
        # import pdb; pdb.set_trace()
        if data["residence_country"] == Countries.objects.get(name="Peru"):
            if "address" not in data:
                raise serializers.ValidationError("address {}".format(required))
        return

    def validate_bussines_client(self, data):
        """Validacion para cuando es juridico."""
        required = _("required")
        error1 = _("can not be a legal person and reside in a foreign country")
        # requerido el nombre de la empresa
        if 'business_name' not in data:
            raise serializers.ValidationError("business_name {}".format(required))
        # requerido el sector economico
        if 'economic_sector' not in data:
            raise serializers.ValidationError("economic_sector {}".format(required))
        # probar si esta vacio
        if data['economic_sector'] is None:
            empty = _("must no be empty")
            raise serializers.ValidationError("economic_sector{}".format(empty))
        # requerido la posicion en la empresa
        if 'position' not in data:
            raise serializers.ValidationError("position {}".format(required))
        if 'address' not in data:
            raise serializers.ValidationError("address {}".format(required))
        # requerido el nombre del representante
        if 'agent_firstname' not in data:
            raise serializers.ValidationError("agent_firstname {}".format(required))
        # requerido el apellido del representante
        if 'agent_lastname' not in data:
            raise serializers.ValidationError("agent_lastname {}".format(required))
        # requerido el ruc del cliente
        if 'ruc' not in data:
            raise serializers.ValidationError("ruc {}".format(required))

        if data["residence_country"] != Countries.objects.get(name="Peru"):
            raise serializers.ValidationError(error1)
        return

    def validate(self, data):
        """Redefinido metodo de validación."""
        if data['type_client'] == 'n':
            self.validate_natural_client(data)

        if data['type_client'] == 'b':
            self.validate_bussines_client(data)
        return data

    def create(self, validated_data):
        """Redefinido metodo de crear cliente."""
        if validated_data["residence_country"] == Countries.objects.get(name="Peru"):
            data_address = validated_data.pop('address')
            address = Address.objects.create(**data_address)
            validated_data['address'] = address
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class SpecialistSerializer(serializers.ModelSerializer):
    """Serializer del especialista."""

    nationality_name = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    nick = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    document_type = serializers.ChoiceField(choices=c.user_document_type)
    document_type_name = serializers.SerializerMethodField()
    type_specialist = serializers.ChoiceField(choices=c.specialist_type_specialist)
    type_specialist_name = serializers.SerializerMethodField()
    address = AddressSerializer()
    email_exact = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    category_name = serializers.SerializerMethodField()
    photo = serializers.CharField(read_only=True)
    ruc = serializers.CharField(required=True)

    class Meta:
        """Modelo del especialista y sus campos."""

        model = Specialist
        fields = (
            'id', 'username', 'nick', 'first_name', 'last_name', 'type_specialist', 'type_specialist_name', 'password',
            'photo', 'document_type', 'document_type_name', 'document_number', 'address', 'ruc', 'email_exact', 'code',
            'telephone', 'cellphone', 'business_name', 'payment_per_answer', 'cv', 'star_rating', 'category',
            'category_name', 'nationality', 'nationality_name')

    def get_nationality_name(self, obj):
        """Devuelvo la nacionalidad del especialista."""
        return _(str(obj.nationality))

    def get_category_name(self, obj):
        """Devuelvo la espacialidad del especialista."""
        return _(str(obj.category))

    def get_document_type_name(self, obj):
        """Devuelve el tipo de documento de identidad del especialista."""
        return _(obj.get_document_type_display())

    def get_type_specialist_name(self, obj):
        """Devuelve el tipo de especialista (Principal/Asociado)."""
        return _(obj.get_type_specialist_display())

    def create(self, validated_data):
        """Redefinido metodo de crear."""
        main = _('Main')
        spec = _('Specialist')
        already = _('already')
        exists = _('exists')
        data_address = validated_data.pop('address')
        address = Address.objects.create(**data_address)
        validated_data['address'] = address
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if validated_data["type_specialist"] == "m" and Specialist.objects.filter(type_specialist="m",
                                                                                  category_id=validated_data[
                                                                                      "category"]).exists():
            output = "%(main)s %(specialist)s %(already)s %(exists)s " % {'main': main, 'specialist': spec,
                                                                          'already': already, 'exists': exists}
            raise serializers.ValidationError(output)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """Metodo actualizar redefinido."""
        main = _('Main')
        spec = _('Specialist')
        already = _('already')
        exists = _('exists')
        category = validated_data.get("category", None)
        instance.nick = validated_data.get('nick', instance.nick)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.type_specialist = validated_data.get('type_specialist', instance.type_specialist)
        instance.document_type = validated_data.get('document_type', instance.document_type)
        instance.document_number = validated_data.get('document_number', instance.document_number)
        instance.email_exact = validated_data.get('email_exact', instance.email_exact)
        instance.telephone = validated_data.get('telephone', instance.telephone)
        instance.cellphone = validated_data.get('cellphone', instance.cellphone)
        instance.ruc = validated_data.get('ruc', instance.ruc)
        instance.business_name = validated_data.get('business_name', instance.business_name)
        instance.payment_per_answer = validated_data.get('payment_per_answer', instance.payment_per_answer)
        instance.category = validated_data.get('category', instance.category)
        if instance.type_specialist == "m" and Specialist.objects.filter(type_specialist="m",
                                                                         category_id=category).exclude(
                                                                         pk=instance.id).exists():
            output = "%(main)s %(specialist)s %(already)s %(exists)s " % {'main': main, 'specialist': spec,
                                                                          'already': already, 'exists': exists}
            raise serializers.ValidationError(output)
        if 'address' in validated_data:
            data_address = validated_data.pop('address')

            # pdb.set_trace()
            address = Address.objects.get(pk=instance.address_id)
            # pdb.set_trace()
            address.department = Department.objects.get(pk=data_address["department"].id)
            address.province = Province.objects.get(pk=data_address["province"].id)
            address.district = District.objects.get(pk=data_address["district"].id)
            address.street = data_address['street']

            address.save()
            instance.address = address
        instance.save()
        return instance


# class AnswerAccountSerializer(serializers.ModelSerializer):
#     date = serializers.SerializerMethodField()
#     time = serializers.SerializerMethodField()
#     time_elapsed = serializers.SerializerMethodField()

#     class Meta:
#         model = Answer
#         fields = ('id','date','time','specialist','created_at','time_elapsed')

#     def get_date(self, obj):
#         return obj.created_at.date()
#     def get_time(self, obj):
#         return str(obj.created_at.hour) + ':' + str(obj.created_at.minute)

#     def get_time_elapsed(self, obj):
#         # d.strftime("%Y-%m-%d %H:%M:%S")
#         date_query = obj.query.created_at
#         date_answer = obj.created_at
#         diff = date_answer - date_query
#         return str(diff)

# class QueryAnswerSerializer(serializers.ModelSerializer):
#     client = serializers.SerializerMethodField()
#     date = serializers.SerializerMethodField()
#     time = serializers.SerializerMethodField()
#     status = serializers.ChoiceField(choices=Query.option_status)
#     answer = serializers.SerializerMethodField()
#     is_delayed = serializers.SerializerMethodField()

#     class Meta:
#         model = Query
#         fields = ('title','client','date','time','status','created_at','answer','is_delayed')

#     def get_date(self,obj):
#         return obj.created_at.date()

#     # Devuelvo la hora y minuto separados
#     def get_time(self,obj):
#         return str(obj.created_at.hour) + ':' + str(obj.created_at.minute)

#     def get_client(self,obj):
#         return obj.client.nick
#     # Devuelvo la respuesta relacionada a la consulta
#     def get_answer(self,obj):
#         answer_related = obj.answer_set.all()
#         return AnswerAccountSerializer(answer_related,many=True).data

#     # Verificar si el tiempo desde que se hizo la consulta fue superado al del
#     # parametro y en base a eso determinar si esta con retraso o a tiempo
#     def get_is_delayed(self,obj):
#         date_query = obj.created_at
#         time_delay = Parameter.objects.get(parameter="time_delay_response")
#         try:
#             answer =  obj.answer_set.get(pk=obj.id)
#             date_elapsed = answer.created_at
#         except:
#             date_elapsed = timezone.now()
#         diff = date_elapsed - date_query
#         days = diff.days*24
#         hours = diff.seconds // 3600
#         if days >= int(time_delay.value) or hours >= int(time_delay.value):
#             return True
#         return False


# # Serializer para consultar estado de .
# class SpecialistAccountSerializer(serializers.ModelSerializer):
#     category = serializers.SlugRelatedField(read_only=True,slug_field='name')
#     query_answer = serializers.SerializerMethodField()
#     photo_category = serializers.SerializerMethodField()

#     class Meta:
#         model = Specialist
#         fields = ('id','first_name','last_name','code','nick','email_exact',
#                   'photo','category','photo_category','payment_per_answer','query_answer')

#         # No son campos editables ya que son de consulta solamente.
#         read_only_fields = ('id','first_name','last_name','code','nick',
#                             'email_exact','photo','category','photo_category',
#                             'query_answer')

#     # Traer por consulta relacionada
#     def get_query_answer(self, obj):
#         answer = obj.query_set.all()
#         return QueryAnswerSerializer(answer,many=True).data

#     def get_photo_category(self,obj):
#         img = obj.category.image
#         return img

# Serializer para traer el listado de vendedores
class SellerSerializer(serializers.ModelSerializer):
    quota = serializers.SerializerMethodField()
    count_plans_seller = serializers.SerializerMethodField()
    count_queries = serializers.SerializerMethodField()
    address = AddressSerializer()

    class Meta:
        model = Seller
        fields = (
            'address', 'count_plans_seller', 'count_queries', 'quota', 'id', 'zone', 'username', 'nick', 'password',
            'first_name', 'last_name', 'email_exact', 'telephone', 'cellphone', 'document_type', 'code',
            'document_number', 'ruc')

    def __init__(self, *args, **kwargs):
        super(SellerSerializer, self).__init__(*args, **kwargs)

    def get_quota(self, obj):
        value = 0

        try:
            today = datetime.datetime.now()
            time_delay = Quota.objects.get(date__year=today.year, date__month=today.month)

            value = time_delay.value
        except Exception as e:
            print(e.args)
        return value

    def get_count_plans_seller(self, obj):
        """
        :param obj:
        :return: cantidad de planes/ventas realizadas por el vendedor
        """
        result = Purchase.objects.filter(seller=obj.id).count()

        return result

    def get_count_queries(self, obj):
        """
        :param obj:
        :return: cantidad de consultas de los productos que ha vendido el usuario vendedor
        """
        result = Purchase.objects.filter(seller__isnull=False, seller=obj.id).aggregate(Sum('query_amount'))

        return result['query_amount__sum']


# Serializer para consultar estado de cuenta del Vendedor.
class SellerAccountSerializer(serializers.ModelSerializer):
    amount_accumulated = serializers.SerializerMethodField()
    fee_accumulated = serializers.SerializerMethodField()
    is_billable = serializers.SerializerMethodField()
    count_products = serializers.SerializerMethodField()
    # A continuacion se definen los campos enviados desde
    # el querySet para que el serializador los reconozca
    purchase__total_amount = serializers.CharField()
    purchase__id = serializers.CharField()
    purchase__code = serializers.CharField()
    purchase__query_amount = serializers.CharField()
    purchase__product__is_billable = serializers.CharField()
    purchase__product__expiration_number = serializers.CharField()
    purchase__product__name = serializers.CharField()
    purchase__client__code = serializers.CharField()
    purchase__client__nick = serializers.CharField()
    purchase__fee__date = serializers.CharField()
    purchase__fee__fee_amount = serializers.CharField()
    purchase__fee__status = serializers.CharField()
    purchase__fee__payment_type__name = serializers.CharField()
    purchase__fee__reference_number = serializers.CharField()
    purchase__fee_number = serializers.CharField()
    purchase__fee__id = serializers.CharField()
    purchase__fee__fee_order_number = serializers.CharField()

    class Meta:
        model = Seller
        fields = ('amount_accumulated', 'fee_accumulated', 'is_billable', 'count_products',
                  # Los campos a continuacion son enviados en el querySet pero han sido
                  # redeclarados para que el serializer los reconozca
                  'purchase__total_amount', 'purchase__id', 'purchase__code', 'purchase__query_amount',
                  'purchase__product__is_billable', 'purchase__product__expiration_number', 'purchase__product__name',
                  'purchase__client__code', 'purchase__client__nick', 'purchase__fee__date',
                  'purchase__fee__fee_amount', 'purchase__fee__id', 'purchase__fee__status',
                  'purchase__fee__payment_type__name', 'purchase__fee__reference_number', 'purchase__fee_number',
                  'purchase__fee__fee_order_number')

    def get_amount_accumulated(self, obj):
        # Esta funcion calcula la sumatoria de los pagos  efectuados en cada cuota,
        # respecto a una venta y fecha especificada
        result = Fee.objects.filter(purchase_id=obj['purchase__id'], date__lte=obj['purchase__fee__date'],
                                    status=obj['purchase__fee__status']).aggregate(Sum('fee_amount'))

        return result['fee_amount__sum']

    def get_fee_accumulated(self, obj):
        # Esta funcion calcula la cantidad de los pagos  efectuados en cada cuota,
        # respecto a una venta y fecha especificada
        result = Fee.objects.filter(purchase_id=obj['purchase__id'], date__lte=obj['purchase__fee__date'],
                                    status=obj['purchase__fee__status']).count()
        return result

    def get_is_billable(self, obj):
        # Retorna si es facturable o no, formato texto
        if obj['purchase__product__is_billable']:
            result = "FAC"
        else:
            result = "NO FAC"

        return result

    def get_count_products(self, obj):
        # Retorna cantidad de productos (de momento se compra ssiemrpe un solo producto)
        return 1


class MediaSerializer(serializers.Serializer):
    photo = serializers.ImageField(max_length=None, required=False, allow_empty_file=False)

    # class Meta:
    #     #model = Specialist
    #     fields = (
    #         'photo',
    #         'filename'
    #     )
