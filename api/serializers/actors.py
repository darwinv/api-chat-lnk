"""Actores/Usuarios (Clientes, Especialistas, Vendedores)."""
from rest_framework import serializers
import random
import datetime
import string
from rest_framework.validators import UniqueValidator
from api.models import User, Client, Countries, SellerContact
from api.models import Address, Department, EconomicSector, Sale
from api.models import Province, District, Specialist, Ciiu, Parameter
from api.models import Seller, LevelInstruction, ObjectionsList, Objection
from django.utils.translation import ugettext_lazy as _
from api.api_choices_models import ChoicesAPI as c
from dateutil.relativedelta import relativedelta
from api.emails import BasicEmailAmazon
from django.http import Http404
from rest_framework.response import Response
from api.utils.tools import capitalize as cap
from api.utils.parameters import Params
from api.utils.validations import document_exists, ruc_exists
from django.contrib.auth.hashers import check_password
from api.utils.querysets import get_queries_pending_to_solve
from django.contrib.auth import password_validation
from api.utils import tools
from collections import OrderedDict

class SpecialistMessageListCustomSerializer(serializers.Serializer):
    """Serializador para devolver datos customizados de un queryset dado."""

    fields = ('photo', 'nick', 'date', 'title', 'total',
              'message', 'client', 'specialist')

    # establecemos que datos del queryset pasado se mostrara
    # en cada campo puesto en la tupla "Fields"

    def to_representation(self, instance):
        """Redefinido metodo de representación."""
        # if isinstance(instance.date, datetime.datetime):
        #     aux_time = instance.date.time()
        # else:
        #     aux_time = instance.date
        return {
                    "client": instance.client,
                    "photo": instance.photo,
                    "displayName": instance.display_name,
                    "specialist": instance.specialist,
                    "title": instance.title,
                    "message": instance.message,
                    "date": instance.date,
                    "id": instance.id,
                    # "total": instance.total
                }


class PendingQueriesSerializer(serializers.Serializer):
    """Serializer para devolver
    las consultas pendientes por accion de un especialista"""

    class Meta:

        fields = ('id', 'title', 'message', 'date_at', 'status')

    def to_representation(self, dicti):
        # import pdb; pdb.set_trace()

        return {"id": dicti["id"],
                "message": dicti["message"],
                "title": dicti["title"],
                "date": str(dicti["date_at"]),
                "status": dicti["status"],
                "specialist_id": dicti["specialist"]
                }


class UserSerializer(serializers.ModelSerializer):
    """

    Serializer que unicamente va ser utilizada para.

    el servicio que devuelve todos los usuarios
    Este servicio es requerido por la web de administracion
    Unicamente expone el id y el nombre de usuario.

    """

    class Meta:

        model = User
        fields = ('id', 'username', 'img_document_number', 'role',
                  'code', 'document_number', 'email_exact')


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('photo',)


class ContactPhotoSerializer(serializers.ModelSerializer):
    "Actualizar foto de contacto"
    class Meta:
        model = SellerContact
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
        if type(obj) is dict:
            return str(obj['department'])
        return str(obj.department)

    def get_province_name(self, obj):
        """Devuelve provincia."""
        if type(obj) is dict:
            return str(obj['province'])
        return str(obj.province)

    def get_district_name(self, obj):
        """Devuelve distrito."""
        if type(obj) is dict:
            return str(obj['district'])
        return str(obj.district)


class ClientSerializer(serializers.ModelSerializer):
    """Serializer del cliente."""

    username = serializers.CharField(validators=[UniqueValidator(
        queryset=User.objects.all())])
    email_exact = serializers.EmailField(validators=[UniqueValidator(
        queryset=User.objects.all())])
    level_instruction_name = serializers.SerializerMethodField()
    nationality = serializers.PrimaryKeyRelatedField(
        queryset=Countries.objects.all(), required=True)
    nationality_name = serializers.SerializerMethodField()
    economic_sector_name = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, min_length=6)
    profession = serializers.CharField(allow_blank=True)
    type_client = serializers.ChoiceField(choices=c.client_type_client)
    type_client_name = serializers.SerializerMethodField()
    sex = serializers.ChoiceField(choices=c.client_sex, allow_blank=True)
    sex_name = serializers.SerializerMethodField()
    document_type = serializers.ChoiceField(choices=c.user_document_type)
    document_type_name = serializers.SerializerMethodField()
    civil_state = serializers.ChoiceField(choices=c.client_civil_state,
                                          allow_blank=True)
    civil_state_name = serializers.SerializerMethodField()
    ocupation = serializers.ChoiceField(choices=c.client_ocupation,
                                        allow_null=True)
    ocupation_name = serializers.SerializerMethodField()
    address = AddressSerializer(required=False)
    nick = serializers.CharField(required=False, allow_blank=True,
                                 allow_null=True)
    residence_country = serializers.PrimaryKeyRelatedField(
        queryset=Countries.objects.all(), required=True)
    residence_country_name = serializers.SerializerMethodField()
    commercial_reason = serializers.CharField(required=False, allow_null=True)
    birthdate = serializers.DateField(required=True)

    photo = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    seller_assigned = serializers.PrimaryKeyRelatedField(
        queryset=Seller.objects.all(), required=False, allow_null=True)

    class Meta:
        """declaracion del modelo y sus campos."""

        model = Client
        fields = (
            'id', 'username', 'nick', 'type_client', 'type_client_name',
            'first_name', 'last_name', 'password', 'photo', 'sex', 'sex_name',
            'document_type', 'document_type_name', 'document_number',
            'civil_state', 'civil_state_name', 'birthdate', 'address', 'ruc',
            'email_exact', 'code', 'telephone', 'cellphone', 'ciiu',
            'activity_description', 'level_instruction',
            'level_instruction_name', 'business_name', 'agent_firstname',
            'agent_lastname', 'position', 'economic_sector',
            'economic_sector_name', 'institute', 'profession', 'ocupation',
            'ocupation_name', 'about', 'nationality', 'nationality_name',
            "residence_country", "commercial_reason", "foreign_address",
            "residence_country_name", "status", "code_cellphone",
            "code_telephone", "role", "seller_assigned")

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
        if obj.ocupation:
            return _(obj.get_ocupation_display())
        return None

    def validate_document_number(self, value):
        """Validar Numero de Documento."""
        data = self.get_initial()
        if data["type_client"] == 'n':
            document_type = data.get('document_type', '0')
            if document_exists(type_doc=document_type, role=data["role"],
                               document_number=data["document_number"]):
                raise serializers.ValidationError(
                    [_('This field must be unique')])
        return value

    def validate_ruc(self, value):
        """Validar Ruc."""
        data = self.get_initial()
        # Se valida solo si es tipo juridico
        if data["type_client"] == 'b':
            if ruc_exists(residence_country=data["residence_country"],
                          role=data["role"], ruc=data["ruc"]):
                raise serializers.ValidationError(
                    [_('This field must be unique')])
        return value

    def validate_birthdate(self, value):
        """Validar Fecha de Nacimiento."""
        data = self.get_initial()
        today = datetime.datetime.today().date()
        min_date = today - relativedelta(years=18)
        if data["type_client"] == 'n':
            if value > min_date:
                raise serializers.ValidationError(
                    [_("You must be of legal age")])
        return value

    def validate_natural_client(self, data):
        """Validacion para cuando es natural."""
        required = _("required")
        # obligatorio el nombre del cliente
        if 'first_name' not in data or not data['first_name']:
            raise serializers.ValidationError({"first_name": [required]})
        # obligatorio el apellido del cliente
        if 'last_name' not in data or not data['last_name']:
            raise serializers.ValidationError({"last_name": [required]})
        # obligatorio el sexo
        if 'sex' not in data or not data['sex']:
            raise serializers.ValidationError({"sex": [required]})
        # obligatorio el estado civil
        if 'civil_state' not in data or not data['civil_state']:
            raise serializers.ValidationError({"civi_state": [required]})
        # obligatorio el nivel de instruccion
        if 'level_instruction' not in data or not data['level_instruction']:
            raise serializers.ValidationError(
                      {"level_instruction": [required]})
        # obligatorio la ocupacion
        if 'ocupation' not in data or not data['ocupation']:
            raise serializers.ValidationError({"ocupation": [required]})
        # si reside en peru la direccion es obligatoria.
        if data["residence_country"] == Countries.objects.get(name="Peru"):
            if "address" not in data or not data["address"]:
                raise serializers.ValidationError({"address": [required]})
        else:
            if ("foreign_address" not in data or
                not data["foreign_address"] or
                    data["foreign_address"] is None):
                raise serializers.ValidationError(
                         {"foreign_address": [required]})
        return

    def validate_bussines_client(self, data):
        """Validacion para cuando es juridico."""
        required = _("required")
        inf_fiscal = _("Tax Code")
        country = Countries.objects.get(name="Peru")
        # requerido el nombre de la empresa
        if 'business_name' not in data or data["business_name"] is None:
            raise serializers.ValidationError({"business_name": [required]})
        # requerido el nombre de la empresa
        if 'commercial_reason' not in data:
            raise serializers.ValidationError(
                      {"commercial_reason": [required]})
        # requerido el sector economico
        if 'economic_sector' not in data or data['economic_sector'] is None:
            raise serializers.ValidationError({"economic_sector": [required]})
        # requerido la posicion en la empresa
        if 'position' not in data or data['position'] is None:
            raise serializers.ValidationError({"position": [required]})
        # si reside en peru la direccion es obligatoria.
        if data["residence_country"] == country:
            if "address" not in data or not data["address"]:
                raise serializers.ValidationError({"address": [required]})
        # sino, la direccion de extranjero es obligatoria
        else:
            if "foreign_address" not in data or not data["foreign_address"]:
                raise serializers.ValidationError(
                          {"foreign_address": [required]})
        # requerido el nombre del representante
        if 'agent_firstname' not in data or data["agent_firstname"] is None:
            raise serializers.ValidationError({"agent_firstname": [required]})
        # requerido el apellido del representante
        if 'agent_lastname' not in data or data["agent_lastname"] is None:
            raise serializers.ValidationError({"agent_lastname": [required]})
        # requerido el ciiu del cliente juridico
        if 'ciiu' not in data or not data["ciiu"]:
            raise serializers.ValidationError({"ciiu": [required]})
        if data["residence_country"] == country:
            if 'ruc' not in data or not data["ruc"]:
                raise serializers.ValidationError([_("required")])
        else:
            if 'ruc' not in data or not data["ruc"]:
                raise serializers.ValidationError({"Tax Code": [required]})
        return

    def validate(self, data):
        if 'request' not in self.context:
            """Redefinido metodo de validación."""
            if data['type_client'] == 'n':
                self.validate_natural_client(data)
                # el codigo sera el numero de documento
                self.context["temp_code"] = data["document_number"]
            if data['type_client'] == 'b':
                self.validate_bussines_client(data)
                # el codigo sera el RUC
                self.context['temp_code'] = data["ruc"]
        elif self.context['request']._request.method == "PUT":
            self.validate_client_put(data)

        else:
            raise serializers.ValidationError({"method": 'don\'t support'})
        return data

    def create(self, validated_data):
        """Redefinido metodo de crear cliente."""
        country_peru = Countries.objects.get(name="Peru")
        validated_data['code'] = str(self.context.get('temp_code')) # El codigo no comienza con C hasta no comprar
        # Verificamos si reside en el extranjero, se elimina direccion
        if validated_data["residence_country"] == country_peru:
            data_address = validated_data.pop('address')
            address = Address.objects.create(**data_address)
            validated_data['address'] = address
        else:
            if 'address' in validated_data:
                del validated_data['address']

        if "seller_assigned" in validated_data and validated_data["seller_assigned"]:
            pass
        else:
            parameter = Parameter.objects.get(parameter="platform_seller")
            validated_data["seller_assigned"] = Seller.objects.get(pk=parameter.value)

        # Si nacionalidad no es peruana, el codigo de usuario se antecede por
        # el iso del pais al que pertenece
        if validated_data["nationality"] != country_peru:
            prefix_country = Countries.objects.get(
                                 pk=validated_data["nationality"].id).iso_code
            validated_data['code'] = prefix_country + validated_data['code']
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """Redefinido metodo de actualizar cliente."""
        country_peru = Countries.objects.get(name="Peru")

        instance.ciiu = validated_data.get('ciiu', instance.ciiu)
        instance.nick = validated_data.get('nick', instance.nick)
        instance.telephone = validated_data.get('telephone', instance.telephone)
        instance.cellphone = validated_data.get('cellphone', instance.cellphone)
        instance.residence_country = validated_data.get('residence_country', instance.residence_country)

        # Verificamos si reside en el extranjero, se elimina direccion
        if 'residence_country' in validated_data:
            if validated_data["residence_country"] == country_peru:
                data_address = validated_data.pop('address')
                address = Address.objects.create(**data_address)
                validated_data['address'] = address
            else:
                instance.address = None
                if 'address' in validated_data:
                    del validated_data['address']

        instance.address = validated_data.get('address', instance.address)
        instance.foreign_address = validated_data.get('foreign_address', instance.foreign_address)

        instance.save()
        return instance

    def validate_client_put(self, data):
        """Validacion para cuando es natural."""
        required = _("required")

        # si reside en peru la direccion es obligatoria.
        if "residence_country" not in data:
            raise serializers.ValidationError({"residence_country": [required]})
        elif data["residence_country"] == Countries.objects.get(name="Peru"):
            if "address" not in data or not data["address"]:
                raise serializers.ValidationError({"address": [required]})
        else:
            if ("foreign_address" not in data or
                not data["foreign_address"] or
                    data["foreign_address"] is None):
                raise serializers.ValidationError(
                         {"foreign_address": [required]})
        return


class SpecialistSerializer(serializers.ModelSerializer):
    """Serializer del especialista."""

    nationality_name = serializers.SerializerMethodField()
    # nick = serializers.CharField(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    document_type = serializers.ChoiceField(choices=c.user_document_type)
    document_type_name = serializers.SerializerMethodField()
    type_specialist = serializers.ChoiceField(
                                  choices=c.specialist_type_specialist)
    type_specialist_name = serializers.SerializerMethodField()
    address = AddressSerializer(required=False)
    email_exact = serializers.EmailField(
                              validators=[UniqueValidator(
                                         queryset=User.objects.all())])
    category_name = serializers.SerializerMethodField()
    photo = serializers.CharField(read_only=True)
    ruc = serializers.CharField(allow_blank=True, required=False)
    residence_country_name = serializers.SerializerMethodField()
    residence_country = serializers.PrimaryKeyRelatedField(
                                    queryset=Countries.objects.all(),
                                    required=True)
    nationality = serializers.PrimaryKeyRelatedField(
                              queryset=Countries.objects.all(),
                              required=True)
    declined = serializers.SerializerMethodField()

    class Meta:
        """Modelo del especialista y sus campos."""

        model = Specialist
        fields = (
            'id', 'username', 'nick', 'first_name', 'last_name',
            'type_specialist', 'type_specialist_name', 'photo',
            'document_type', 'document_type_name', 'document_number',
            'address', 'ruc', 'email_exact', 'code', 'telephone', 'cellphone',
            'business_name', 'payment_per_answer', 'cv', 'star_rating',
            'category', 'category_name', 'nationality', 'nationality_name',
            'residence_country', 'residence_country_name',
            'foreign_address', 'role', 'declined')

    def get_nationality_name(self, obj):
        """Devuelvo la nacionalidad del especialista."""
        return _(str(obj.nationality))

    def get_residence_country_name(self, obj):
        """Devuelvo la residencia del especialista."""
        return _(str(obj.residence_country))

    def get_category_name(self, obj):
        """Devuelvo la espacialidad del especialista."""
        return _(str(obj.category))

    def get_document_type_name(self, obj):
        """Devuelve el tipo de documento de identidad del especialista."""
        return _(obj.get_document_type_display())

    def get_type_specialist_name(self, obj):
        """Devuelve el tipo de especialista (Principal/Asociado)."""
        return _(obj.get_type_specialist_display())

    def get_declined(self, obj):
        if hasattr(obj, 'declined') and obj.declined:
            return True
        return False

    def validate_document_number(self, value):
        """Validar Numero de Documento."""
        data = self.get_initial()
        document_type = data.get('document_type', '0')

        if self.instance and self.instance.document_number == value:
            return value

        if document_exists(type_doc=document_type, role=data["role"],
                           document_number=data["document_number"]):
                raise serializers.ValidationError(
                    [_('This field must be unique')])
        return value

    def create(self, validated_data):
        """Redefinido metodo de crear."""
        valid_spec = _('Main Specialist already exists for this speciality')
        country_peru = Countries.objects.get(name="Peru")
        # validar si el ruc ya existe
        if ruc_exists(residence_country=validated_data["residence_country"],
                      role=validated_data["role"],
                      ruc=validated_data["ruc"]):
            raise serializers.ValidationError(
                        {'ruc': [_('This field must be unique')]})

        if validated_data["nationality"] != country_peru:
            validated_data['code'] = Countries.objects.get(
                pk=validated_data["nationality"].id).iso_code + validated_data["code"]

        # Si la residencia es peru, se crea el address
        if validated_data["residence_country"] == country_peru:
            data_address = validated_data.pop('address')
            address = Address.objects.create(**data_address)
            validated_data['address'] = address
        else:
            if 'address' in validated_data:
                del validated_data['address']
        # si se encuentra y esta vacio, se debe borrar para guardar null
        if 'ruc' in validated_data:
            if not validated_data['ruc']:
                del validated_data['ruc']

        password = ''.join(
              random.SystemRandom().choice(
                string.ascii_uppercase + string.digits) for _ in range(10))
        # validated_data['key'] = password
        validated_data['key'] = "123456"
        validated_data['status'] = 1
        instance = self.Meta.model(**validated_data)
        # "ruc {}".format(required)
        if (validated_data["type_specialist"] == "m" and
            Specialist.objects.filter(
                type_specialist="m",
                category_id=validated_data["category"]).exists()):
            raise serializers.ValidationError(
                {"type_specialist": [valid_spec]})
        if password is not None:
            # instance.set_password(password)
            instance.set_password("123456")
        instance.save()

        mail = BasicEmailAmazon(subject='Envio Credenciales',
                                to=validated_data["email_exact"],
                                template='email/send_credentials')


        credentials = {}
        credentials["user"] = validated_data["username"]
        credentials["pass"] = password
        mail.sendmail(args=credentials)
        return instance

    def update(self, instance, validated_data):
        """Metodo actualizar redefinido."""
        valid_spec = _('Main Specialist already exists for this speciality')
        category = validated_data.get("category", None)
        instance.nick = validated_data.get('nick', instance.nick)
        instance.first_name = validated_data.get('first_name',
                                                 instance.first_name)
        instance.last_name = validated_data.get('last_name',
                                                instance.last_name)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.type_specialist = validated_data.get('type_specialist',
                                                      instance.type_specialist)
        instance.document_type = validated_data.get('document_type',
                                                    instance.document_type)
        instance.document_number = validated_data.get('document_number',
                                                      instance.document_number)
        instance.telephone = validated_data.get('telephone',
                                                instance.telephone)
        instance.cellphone = validated_data.get('cellphone',
                                                instance.cellphone)
        instance.ruc = validated_data.get('ruc', instance.ruc)
        instance.business_name = validated_data.get('business_name',
                                                    instance.business_name)
        instance.payment_per_answer = validated_data.get(
                        'payment_per_answer', instance.payment_per_answer)
        instance.category = validated_data.get('category', instance.category)
        instance.residence_country = validated_data.get(
                        'residence_country', instance.residence_country)
        instance.nationality = validated_data.get('nationality',
                                                  instance.nationality)
        instance.code = validated_data.get('code',
                                                instance.code)

        if (instance.type_specialist == "m"
            and Specialist.objects.filter(type_specialist="m",
                                          category_id=category).exclude(
                                              pk=instance.id).exists()):

            raise serializers.ValidationError(
                                             {"type_specialist": [valid_spec]})

        # Si la residencia es peru, se crea el address
        if ("residence_country" in validated_data
            and validated_data["residence_country"] == Countries.objects.get(
                name="Peru")):
            if 'address' in validated_data:
                data_address = validated_data.pop('address')

                # si el usuario tenia previamente una direccion registrada
                if instance.address_id:
                    # pdb.set_trace()
                    address = Address.objects.get(pk=instance.address_id)
                    # pdb.set_trace()
                    address.department = Department.objects.get(
                            pk=data_address["department"].id)
                    address.province = Province.objects.get(
                            pk=data_address["province"].id)
                    address.district = District.objects.get(
                            pk=data_address["district"].id)
                    address.street = data_address['street']

                    address.save()
                else:
                    address = Address.objects.create(
                        department=Department.objects.get(
                            pk=data_address["department"].id),
                        province=Province.objects.get(
                            pk=data_address["province"].id),
                        district=District.objects.get(
                            pk=data_address["district"].id),
                        street=data_address["street"])

                instance.address = address
        else:
            if 'foreign_address' in validated_data:
                instance.foreign_address = validated_data.get(
                    'foreign_address', instance.foreign_address)
            instance.address = None

        instance.save()
        return instance

    def validate(self, data):
        """Redefinido metodo de validación."""
        required = _('required')
        # si la residencia es peru, es obligatoria la dirección
        if self.context['request']._request.method == 'POST':
            if "residence_country" in data and data["residence_country"] == Countries.objects.get(name="Peru"):
                if 'address' not in data:
                    raise serializers.ValidationError(
                        "address {}".format(required))
                if 'ruc' not in data:
                    raise serializers.ValidationError(
                        "ruc {}".format(required))
            elif "foreign_address" not in data or not data["foreign_address"]:
                raise serializers.ValidationError(
                    "foreign_address {}".format(required))

        return data


class AssociateSpecialistSerializer(SpecialistSerializer):
    """Listado de Especialistas Asociados."""
    def to_representation(self, instance):
        # import pdb; pdb.set_trace()
        pending = get_queries_pending_to_solve(specialist=instance)
        ret = super().to_representation(instance)
        ret["pending_queries_to_solve"] = pending
        return ret

# Serializer para traer el listado de vendedores
class SellerSerializer(serializers.ModelSerializer):
    """Serializer de Vendedor."""

    nationality_name = serializers.SerializerMethodField()
    quota = serializers.SerializerMethodField()
    address = AddressSerializer(required=False)
    document_type = serializers.ChoiceField(choices=c.user_document_type)
    document_type_name = serializers.SerializerMethodField()
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    ruc = serializers.CharField(allow_blank=True, allow_null=True,
                                required=False)
    email_exact = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    nationality = serializers.PrimaryKeyRelatedField(
        queryset=Countries.objects.all(), required=True)
    residence_country = serializers.PrimaryKeyRelatedField(
        queryset=Countries.objects.all(), required=True)
    residence_country_name = serializers.SerializerMethodField()
    ciiu_name = serializers.SerializerMethodField()
    photo = serializers.CharField(read_only=True)

    class Meta:
        """Meta de Vendedor."""

        model = Seller
        fields = (
            'id', 'address', 'quota', 'zone', 'username', 'nick', 'first_name',
            'last_name', 'email_exact', 'telephone', 'cellphone', "photo",
            'document_type', 'document_type_name', 'code', 'document_number',
            'ruc', 'nationality', 'nationality_name', 'residence_country',
            'residence_country_name', "foreign_address", "ciiu", "ciiu_name",
            "role")

    def get_nationality_name(self, obj):
        """Devuelvo la nacionalidad del vendedor."""
        return _(str(obj.nationality))

    def get_ciiu_name(self, obj):
        """Devuelvo la nacionalidad del vendedor."""
        try:
            return _(str(obj.ciiu.description))
        except Exception as e:
            return None

    def get_residence_country_name(self, obj):
        """Devuelve resiencia del cliente."""
        return _(str(obj.residence_country))

    def get_document_type_name(self, obj):
        """Devuelve el tipo de documento de identidad."""
        return _(obj.get_document_type_display())

    def validate(self, data):
        """Redefinido metodo de validación."""
        required = _('required')
        address = _('address')
        # si la residencia es peru, es obligatoria la dirección
        if not self.instance:
            if data["residence_country"] == Countries.objects.get(name="Peru"):
                if 'address' not in data:
                    raise serializers.ValidationError(
                        "{} {}".format(address, required))
            else:
                if "foreign_address" not in data or not data["foreign_address"]:
                    raise serializers.ValidationError(
                            "{} {}".format(address, required))
        return data

    def update(self, instance, validated_data):
        """Metodo actualizar redefinido."""
        instance.residence_country = validated_data.get(
            'residence_country', instance.residence_country)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.nick = validated_data.get(
            'nick', instance.nick)
        instance.photo = validated_data.get(
            'photo', instance.photo)
        instance.document_type = validated_data.get(
            'document_type', instance.document_type)
        instance.document_number = validated_data.get(
            'document_number', instance.document_number)
        instance.ciiu = validated_data.get('ciiu', instance.ciiu)
        instance.email_exact = validated_data.get(
            'email_exact', instance.email_exact)
        instance.cellphone = validated_data.get(
            'cellphone', instance.cellphone)
        instance.telephone = validated_data.get(
            'telephone', instance.telephone)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)

        if "residence_country" in validated_data and validated_data["residence_country"] == Countries.objects.get(name="Peru"):
            if 'address' in validated_data:
                data_address = validated_data.pop('address')
                # si el usuario tenia previamente una direccion registrada
                if instance.address_id:
                    # pdb.set_trace()
                    address = Address.objects.get(pk=instance.address_id)
                    # pdb.set_trace()
                    address.department = Department.objects.get(
                        pk=data_address["department"].id)
                    address.province = Province.objects.get(
                        pk=data_address["province"].id)
                    address.district = District.objects.get(
                        pk=data_address["district"].id)
                    address.street = data_address['street']
                    address.save()
                else:
                    address = Address.objects.create(department= Department.objects.get(pk=data_address["department"].id),
                                                     province= Province.objects.get(pk=data_address["province"].id),
                                                     district= District.objects.get(pk=data_address["district"].id),
                                                     street= data_address["street"])#
                instance.address = address
        else:
            if 'foreign_address' in validated_data:
                instance.foreign_address = validated_data.get('foreign_address', instance.foreign_address)
            instance.address = None

        instance.save()
        return instance

    def create(self, validated_data):
        """Redefinido metodo de crear vendedor."""
        country_peru = Countries.objects.get(name="Peru")
        if document_exists(type_doc=validated_data["document_type"],
                           role=validated_data["role"],
                           document_number=validated_data["document_number"]):
            raise serializers.ValidationError(
                        {'document_number': [_('This field must be unique')]})

        if validated_data["nationality"] != country_peru:
            prefix_country = Countries.objects.get(pk=validated_data["nationality"].id).iso_code
            validated_data['code'] = prefix_country + validated_data['code']

        if 'ruc' in validated_data and validated_data['ruc']:
            if ruc_exists(residence_country=validated_data["residence_country"],
                          role=validated_data["role"],
                          ruc=validated_data["ruc"]):
                raise serializers.ValidationError(
                        {'ruc': [_('This field must be unique')]})
        # si la residencia es peru, se crea la instancia de la dirección
        if validated_data["residence_country"] == country_peru:
            data_address = validated_data.pop('address')
            address = Address.objects.create(**data_address)
            validated_data['address'] = address
        elif 'address' in validated_data:
            del validated_data['address']

        # si se encuentra y esta vacio, se debe borrar
        if 'ruc' in validated_data:
            if not validated_data['ruc'] or validated_data['ruc'] is None:
                del validated_data['ruc']
        password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        # validated_data['key'] = password
        validated_data['key'] = "123456"
        validated_data['status'] = 1
        instance = self.Meta.model(**validated_data)
        if password is not None:
            # instance.set_password(password)
            instance.set_password("123456")
        instance.save()
        mail = BasicEmailAmazon(subject='Envio Credenciales', to=validated_data["email_exact"],
                                template='email/send_credentials')
        credentials = {}
        credentials["user"] = validated_data["email_exact"]
        credentials["pass"] = password
        mail.sendmail(args=credentials)
        return instance

    def __init__(self, *args, **kwargs):
        super(SellerSerializer, self).__init__(*args, **kwargs)

    def get_quota(self, obj):
        value = 0

        try:
            today = datetime.datetime.now()
            time_delay = Quota.objects.get(date__year=today.year, date__month=today.month)

            value = time_delay.value
        except Exception as e:
            print("error get_quota")
            print(e.args)
        return value

    # def get_count_plans_seller(self, obj):
    #     """
    #     :param obj:
    #     :return: cantidad de planes/ventas realizadas por el vendedor
    #     """
    #     result = Purchase.objects.filter(seller=obj.id).count()
    #
    #     return result

    # def get_count_queries(self, obj):
    #     """
    #     :param obj:
    #     :return: cantidad de consultas de los productos que ha vendido el usuario vendedor
    #     """
    #     result = Purchase.objects.filter(seller__isnull=False, seller=obj.id).aggregate(Sum('query_amount'))
    #
    #     return result['query_amount__sum']


# Serializer para consultar estado de cuenta del Vendedor.
# class SellerAccountSerializer(serializers.ModelSerializer):
#     amount_accumulated = serializers.SerializerMethodField()
#     fee_accumulated = serializers.SerializerMethodField()
#     is_billable = serializers.SerializerMethodField()
#     count_products = serializers.SerializerMethodField()
#     # A continuacion se definen los campos enviados desde
#     # el querySet para que el serializador los reconozca
#     purchase__total_amount = serializers.CharField()
#     purchase__id = serializers.CharField()
#     purchase__code = serializers.CharField()
#     purchase__query_amount = serializers.CharField()
#     purchase__product__is_billable = serializers.CharField()
#     purchase__product__expiration_number = serializers.CharField()
#     purchase__product__name = serializers.CharField()
#     purchase__client__code = serializers.CharField()
#     purchase__client__nick = serializers.CharField()
#     purchase__fee__date = serializers.CharField()
#     purchase__fee__fee_amount = serializers.CharField()
#     purchase__fee__status = serializers.CharField()
#     purchase__fee__payment_type__name = serializers.CharField()
#     purchase__fee__reference_number = serializers.CharField()
#     purchase__fee_number = serializers.CharField()
#     purchase__fee__id = serializers.CharField()
#     purchase__fee__fee_order_number = serializers.CharField()
#
#     class Meta:
#         model = Seller
#         fields = ('amount_accumulated', 'fee_accumulated', 'is_billable', 'count_products',
#                   # Los campos a continuacion son enviados en el querySet pero han sido
#                   # redeclarados para que el serializer los reconozca
#                   'purchase__total_amount', 'purchase__id', 'purchase__code', 'purchase__query_amount',
#                   'purchase__product__is_billable', 'purchase__product__expiration_number', 'purchase__product__name',
#                   'purchase__client__code', 'purchase__client__nick', 'purchase__fee__date',
#                   'purchase__fee__fee_amount', 'purchase__fee__id', 'purchase__fee__status',
#                   'purchase__fee__payment_type__name', 'purchase__fee__reference_number', 'purchase__fee_number',
#                   'purchase__fee__fee_order_number')
#
#     def get_amount_accumulated(self, obj):
#         # Esta funcion calcula la sumatoria de los pagos  efectuados en cada cuota,
#         # respecto a una venta y fecha especificada
#         result = Fee.objects.filter(purchase_id=obj['purchase__id'], date__lte=obj['purchase__fee__date'],
#                                     status=obj['purchase__fee__status']).aggregate(Sum('fee_amount'))
#
#         return result['fee_amount__sum']
#
#     def get_fee_accumulated(self, obj):
#         # Esta funcion calcula la cantidad de los pagos  efectuados en cada cuota,
#         # respecto a una venta y fecha especificada
#         result = Fee.objects.filter(purchase_id=obj['purchase__id'], date__lte=obj['purchase__fee__date'],
#                                     status=obj['purchase__fee__status']).count()
#         return result
#
#     def get_is_billable(self, obj):
#         # Retorna si es facturable o no, formato texto
#         if obj['purchase__product__is_billable']:
#             result = "FAC"
#         else:
#             result = "NO FAC"
#
#         return result
#
#     def get_count_products(self, obj):
#         # Retorna cantidad de productos (de momento se compra ssiemrpe un solo producto)
#         return 1

class ListObjectionsSerializer(serializers.ModelSerializer):
    """Servicio para validar los motivos de objecion."""

    name = serializers.SerializerMethodField()

    class Meta:
        """Modelo"""
        model = ObjectionsList
        fields = ('name',)

    def get_name(self, obj):
        """Devuelve nacionalidad del cliente."""
        return _(str(obj.objection))


class SellerContactSerializer(serializers.ModelSerializer):
    """Serializer Contacto."""

    name = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()

    class Meta:
        """ Model Contacto."""
        model = SellerContact
        fields = ('id', 'photo', 'name', 'document_type',
                  'type_contact', 'latitude', 'longitude',
                  'type_client', 'document')

    def get_name(self, obj):
        """Devuelve nombre del cliente."""
        if obj.type_client == 'n':
            return obj.first_name + ' ' + obj.last_name
        else:
            return obj.agent_firstname + ' ' + obj.agent_lastname

    def get_document(self, obj):
        """Devuelvo el documento."""
        if obj.type_client == 'b':
            return obj.ruc
        else:
            return obj.document_number


class SellerFilterContactSerializer(serializers.ModelSerializer):
    """Serializer de contacto filtrado."""
    address = AddressSerializer(required=False)
    client_id = serializers.SerializerMethodField()
    have_sale = serializers.SerializerMethodField()

    class Meta:
        """ Model Contacto."""
        model = SellerContact
        fields = '__all__'

    def get_client_id(self, obj):
        """Devuelve cliente id"""
        try:
            client = Client.objects.get(email_exact=obj.email_exact)
            client_id = client.id
        except Client.DoesNotExist:
            client_id = None
        return client_id

    def get_have_sale(self, obj):
        """Devuelve si contacto tiene compra"""
        try:
            client = Client.objects.get(email_exact=obj.email_exact)
            client_id = client.id
        except Client.DoesNotExist:
            client_id = False

        if client_id:
            sale = Sale.objects.filter(client=client_id)
            if sale:
                return True
        return False

class ObjectionsContactSerializer(serializers.ModelSerializer):
    """Lista de objeciones del serializer del contacto."""

    def to_representation(self, obj):
        data = {}
        if obj.type_contact == 2:
            objections = ListObjectionsSerializer(
                obj.objectionslist_set.all(), many=True).data
            data["objections"] = objections
            if obj.other_objection:
                other = OrderedDict()
                other['name'] = obj.other_objection
                data["objections"].append(other)
        return data


class ContactToClientSerializer(serializers.ModelSerializer):
    """Pasar de Contacto a Cliente."""
    email_exact = serializers.EmailField(required=True)

    class Meta:
        """ Model Contacto."""
        model = SellerContact
        fields = ('email_exact',)

    def create(self, validated_data):
        email = validated_data["email_exact"]
        try:
            contact = SellerContact.objects.get(email_exact=email)
        except SellerContact.DoesNotExist:
            raise Http404

        data_client = SellerContact.objects.filter(
            email_exact=email).values().first()
        # import pdb; pdb.set_trace()
        data_client["username"] = email
        data_client["role"] = Params.ROLE_CLIENT
        data_client['seller_assigned'] = contact.seller
        password = ''.join(random.SystemRandom().choice(string.digits) for _ in range(6))
        data_client["password"] = password
        data_client["password"] = "123456"  # CREAR CONTRASEÑA GENERICA
        data_client["nationality"] = contact.nationality_id
        data_client["residence_country"] = contact.residence_country_id
        data_client["level_instruction"] = contact.level_instruction_id
        data_client["address"] = AddressSerializer(contact.address).data
        data_client["photo"] = contact.photo

        if data_client["type_client"] == 'b':
            data_client['birthdate'] = '1900-01-01'
            data_client['sex'] = ''
            data_client['civil_state'] = ''
            data_client['level_instruction'] = ''
            data_client['profession'] = ''
            data_client['ocupation'] = None
            data_client['last_name'] = ''
            data_client['first_name'] = ''
            data_client['economic_sector'] = contact.economic_sector_id
            data_client['ciiu'] = contact.ciiu_id

        serializer_client = ClientSerializer(data=data_client)
        if serializer_client.is_valid():
            serializer_client.save()
            self.context['client_id'] = serializer_client.data['id']

            mail = BasicEmailAmazon(subject='Envio Credenciales', to=data_client["username"],
                                    template='email/send_credentials')
            credentials = {}
            credentials["user"] = data_client["username"]
            credentials["pass"] = password
            mail.sendmail(args=credentials)

        else:
            raise serializers.ValidationError(serializer_client.errors)
        return contact

    def to_representation(self, instance):
        """To Repr."""

        client_id = self.context['client_id']
        return {"client_id": client_id}


class BaseSellerContactSerializer(serializers.ModelSerializer):
    """Base para contacto."""

    def to_representation(self, obj):
        """Redefinido metodo de representación del serializer."""
        data = {
            "id": obj.id, "type_contact": obj.type_contact,
            "first_name": obj.first_name, "last_name": obj.last_name,
            "document_type": obj.document_type,
            "document_number": obj.document_number
        }
        # serializamos la lista de objeciones si es no efectivo
        if obj.type_contact == 2:
            objections = ListObjectionsSerializer(
                obj.objectionslist_set.all(), many=True).data
            data["objections"] = objections
            if obj.other_objection:
                other = OrderedDict()
                other['name'] = obj.other_objection
                data["objections"].append(other)

        # Id de cliente creado
        if 'client_id' in self.context:
            data['client_id'] = self.context['client_id']
        else:
            data['client_id'] = None

        return data

    def validate(self, data):
        """Validate."""
        required = _("required")
        # si reside en peru la direccion es obligatoria.
        if data["residence_country"] == Countries.objects.get(name="Peru"):
            if "address" not in data or not data["address"]:
                raise serializers.ValidationError({"address": [required]})
        else:
            if ("foreign_address" not in data or
                not data["foreign_address"] or
                    data["foreign_address"] is None):
                raise serializers.ValidationError(
                         {"foreign_address": [required]})

        if data["type_contact"] == 2:
            if 'objection' not in data and 'other_objection' not in data:
                raise serializers.ValidationError(
                    _("the objection is required"))
        else:
            if 'password' not in data:
                raise serializers.ValidationError(_("password required"))
        return data

    def create(self, validated_data):
        """Redefinido metodo de crear contacto."""
        country_peru = Countries.objects.get(name="Peru")
        # Verificamos si reside en el extranjero, se elimina direccion
        if validated_data["residence_country"] == country_peru:
            data_address = validated_data.pop('address')
            address = Address.objects.create(**data_address)
            validated_data['address'] = address
        else:
            if 'address' in validated_data:
                del validated_data['address']

        if 'password' in validated_data:
            password = validated_data.pop('password')

        if 'objection' in validated_data:
            objection_list = validated_data.pop('objection')

        type_contact_temp = validated_data["type_contact"]
        validated_data["type_contact"] = 2
        instance = self.Meta.model(**validated_data)
        # creo el listado de objeciones si es no efectivo

        if type_contact_temp == 2:
            instance.save()
            if 'objection_list' in locals():
                for objection in objection_list:
                    # objection_obj = Objection.objects.get(pk=objection)
                    ObjectionsList.objects.create(contact=instance,
                                                  objection=objection)
        else:
            # registro de cliente si es efectivo
            data_client = self.get_initial()
            data_client["username"] = data_client["email_exact"]
            data_client["role"] = Params.ROLE_CLIENT
            data_client['password'] = password
            data_client['seller_assigned'] = data_client['seller']

            if data_client["type_client"] == 'b':
                data_client['birthdate'] = '1900-01-01'
                data_client['sex'] = ''
                data_client['civil_state'] = ''
                data_client['level_instruction'] = ''
                data_client['profession'] = ''
                data_client['ocupation'] = None
            serializer_client = ClientSerializer(data=data_client)

            if serializer_client.is_valid():
                serializer_client.save()
                instance.save()
                self.context['client_id'] = serializer_client.data['id']
            else:
                raise serializers.ValidationError(serializer_client.errors)
        return instance


class SellerContactNaturalSerializer(BaseSellerContactSerializer):
    """Serializer de Contacto No Efectivo (tipo natural)."""

    first_name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    last_name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    latitude = serializers.CharField(required=True, allow_blank=False)
    longitude = serializers.CharField(required=True, allow_blank=False)
    type_contact = serializers.ChoiceField(choices=c.type_seller_contact)
    type_contact_name = serializers.SerializerMethodField()
    type_client = serializers.ChoiceField(choices=c.client_type_client)
    document_type = serializers.ChoiceField(choices=c.user_document_type)
    document_number = serializers.CharField(validators=[UniqueValidator(queryset=SellerContact.objects.filter(type_client='n'))])
    document_type_name = serializers.SerializerMethodField()
    email_exact = serializers.EmailField(validators=[UniqueValidator(queryset=SellerContact.objects.all())])
    civil_state = serializers.ChoiceField(choices=c.client_civil_state)
    civil_state_name = serializers.SerializerMethodField()
    sex = serializers.ChoiceField(choices=c.client_sex)
    sex_name = serializers.SerializerMethodField()
    ocupation = serializers.ChoiceField(choices=c.client_ocupation)
    ocupation_name = serializers.SerializerMethodField()
    address = AddressSerializer(required=False)
    birthdate = serializers.DateField(required=True)
    photo = serializers.CharField(read_only=True)
    objection_name = serializers.SerializerMethodField()
    objection = serializers.ListField(child=serializers.PrimaryKeyRelatedField(
        queryset=Objection.objects.all()), write_only=True, required=False)
    level_instruction = serializers.PrimaryKeyRelatedField(
        queryset=LevelInstruction.objects.all(), required=True)
    level_instruction_name = serializers.SerializerMethodField()
    nationality = serializers.PrimaryKeyRelatedField(
        queryset=Countries.objects.all(), required=True)
    nationality_name = serializers.SerializerMethodField()
    residence_country = serializers.PrimaryKeyRelatedField(
        queryset=Countries.objects.all(), required=True)
    password = serializers.CharField(required=False)

    class Meta:
        """Meta de Contacto."""

        model = SellerContact
        fields = ('id', 'first_name', 'last_name', 'type_contact',
                  'type_contact_name', 'document_type', 'document_type_name',
                  'document_number', 'email_exact', 'type_client', 'civil_state',
                  'civil_state_name', 'birthdate', 'institute', 'objection',
                  'sex', 'sex_name', 'ocupation_name', 'activity_description',
                  'photo', 'about', 'cellphone', 'telephone', 'ocupation',
                  'profession', 'address', 'level_instruction', 'latitude',
                  'longitude', 'seller', 'objection_name', 'nationality',
                  'nationality_name', 'level_instruction_name', 'photo',
                  "foreign_address", 'residence_country',
                  'password', 'other_objection'
                  )
        # extra_kwargs = {
        #         'objection': {'write_only': True},
        # }

    def get_level_instruction_name(self, obj):
        """Devuelve nivel de instrucción."""
        return _(str(obj.level_instruction))

    def get_nationality_name(self, obj):
        """Devuelve nacionalidad del cliente."""
        return _(str(obj.nationality))

    def get_objection_name(self, obj):
        """Devuelve objecion del contacto."""
        return _(str(obj.objection))

    # se devuelve el valor leible y traducido
    def get_type_contact_name(self, obj):
        """Devuelve tipo de cliente (Natural/Juridico)."""
        return _(obj.get_type_contact_display())

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



class SellerContactBusinessSerializer(BaseSellerContactSerializer):
    """Serializer de Contacto No Efectivo (tipo juridico)."""

    business_name = serializers.CharField(required=True,
                                          allow_blank=False,
                                          allow_null=False)
    commercial_reason = serializers.CharField(required=True,
                                              allow_blank=False,
                                              allow_null=False)
    email_exact = serializers.EmailField(validators=[UniqueValidator(queryset=SellerContact.objects.all())])
    address = AddressSerializer(required=False)
    ruc = serializers.CharField(required=True, validators=[UniqueValidator(queryset=SellerContact.objects.filter(type_client='b'))])
    latitude = serializers.CharField(required=True, allow_blank=False)
    longitude = serializers.CharField(required=True, allow_blank=False)
    type_contact = serializers.ChoiceField(choices=c.type_seller_contact)
    type_contact_name = serializers.SerializerMethodField()
    type_client = serializers.ChoiceField(choices=c.client_type_client)
    document_type = serializers.ChoiceField(choices=c.user_document_type)
    document_type_name = serializers.SerializerMethodField()
    ciiu = serializers.PrimaryKeyRelatedField(queryset=Ciiu.objects.all(), required=True)
    photo = serializers.CharField(read_only=True)
    objection_name = serializers.SerializerMethodField()
    objection = serializers.ListField(child=serializers.PrimaryKeyRelatedField(
        queryset=Objection.objects.all()), write_only=True, required=False)
    agent_firstname = serializers.CharField(max_length=45, allow_blank=False, allow_null=False)
    agent_lastname = serializers.CharField(max_length=45, allow_blank=False, allow_null=False)
    position = serializers.CharField(max_length=45, allow_null=True)
    objection_name = serializers.SerializerMethodField()
    nationality = serializers.PrimaryKeyRelatedField(queryset=Countries.objects.all(), required=True)
    nationality_name = serializers.SerializerMethodField()
    economic_sector = serializers.PrimaryKeyRelatedField(queryset=EconomicSector.objects.all(), required=True)
    residence_country = serializers.PrimaryKeyRelatedField(
        queryset=Countries.objects.all(), required=True)
    password = serializers.CharField(required=False)

    class Meta:
        """Meta de Contacto."""

        model = SellerContact
        fields = ('id', 'business_name', 'commercial_reason', 'type_contact',
                  'document_type', 'document_type_name', 'document_number',
                  'ruc', 'economic_sector', 'activity_description', 'about',
                  'cellphone', 'telephone', 'address', 'latitude', 'position',
                  'type_client', 'longitude', 'seller', 'objection', 'email_exact',
                  'objection_name', 'nationality', 'type_contact_name',
                  'nationality_name', 'photo', 'agent_firstname', 'objection',
                  'agent_lastname', 'residence_country', 'password', 'ciiu',
                  'other_objection', "foreign_address"
                  )

    def get_nationality_name(self, obj):
        """Devuelve nacionalidad del cliente."""
        return _(str(obj.nationality))

    def get_objection_name(self, obj):
        """Devuelve objecion del contacto."""
        return _(str(obj.objection))

    # se devuelve el valor leible y traducido
    def get_type_contact_name(self, obj):
        """Devuelve tipo de cliente (Natural/Juridico)."""
        return _(obj.get_type_contact_display())

    def get_document_type_name(self, obj):
        """Devuelve tipo de documento de identidad."""
        return _(obj.get_document_type_display())


class MediaSerializer(serializers.Serializer):
    photo = serializers.ImageField(max_length=None, required=False, allow_empty_file=False)

    img_document_number = serializers.ImageField(
        max_length=None,
        required=False,
        allow_empty_file=False)


class KeySerializer(serializers.ModelSerializer):
    """Serializer devuelve clave."""

    class Meta:
        """Meta."""

        model = User
        fields = ("id", "username", "key")
        read_only_fields = fields


class ChangePassword(serializers.ModelSerializer):
    """Cambiar clave de usuario."""
    old_password = serializers.CharField(required=True)

    class Meta:
        """Meta."""

        model = User
        fields = ("id", "password", 'old_password')
        extra_kwargs = {
                'password': {'write_only': True},
                'old_password': {'write_only': True}
        }

    def validate_old_password(self, value):
        """Check if password  is correct."""
        error = _("old password is invalid")
        if check_password(value, self.instance.password):
            return value
        else:
            raise serializers.ValidationError(error)

    def update(self, instance, validated_data):
        """Redefinir update."""
        password = validated_data.pop('password', None)
        instance.key = password
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def to_representation(self, obj):
        return {}


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Cambiar clave de usuario (solos dev)."""

    class Meta:
        """Meta."""

        model = User
        fields = ("id", "password", 'key')
        extra_kwargs = {
                'password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        """Redefinir update."""
        password = validated_data.pop('password', None)
        instance.key = password
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class ChangeEmailSerializer(serializers.ModelSerializer):
    """Cambiar clave de usuario."""

    email_exact = serializers.EmailField(validators=[UniqueValidator(
        queryset=User.objects.all())])
    old_password = _("old password is invalid")

    class Meta:
        """Meta."""
        model = User
        fields = ("id", "email_exact", "password")
        extra_kwargs = {'email_exact': {'required': True},'password': {'required': True,'write_only': True} }

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError(self.old_password)

        return value

    def update(self, instance, validated_data):
        """Redefinir update."""
        required = _("required")
        email_exact = validated_data.pop('email_exact', None)
        password = validated_data.pop('password', None)

        if not email_exact:
            raise serializers.ValidationError({"email_exact":required})
        if not password:
            raise serializers.ValidationError({"password":required})

        instance.email_exact = email_exact
        instance.username = email_exact
        instance.email = email_exact
        instance.save()
        return instance


# AddressSerializer
#     fields = ('street', 'department', 'province', 'district')


class RucApiDetailSerializer(serializers.Serializer):
    """Detalle por Ruc."""
    business_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    commercial_reason = serializers.CharField()
    telephone = serializers.CharField()
    cellphone = serializers.CharField()
    ruc = serializers.CharField()

    def get_address(self, obj):
        address = {}
        try:
            if 'departamento' in obj:
                try:
                    department = Department.objects.get(name=obj['departamento'])
                    address['department'] = department
                except Department.DoesNotExist:
                    address['department'] = None
            else:
                address['department'] = None

            if 'provincia' in obj:
                try:
                    province = Province.objects.get(name=obj['provincia'],
                                                    department=address['department'])
                    address['province'] = province
                except Province.DoesNotExist:
                    address['province'] = None
            else:
                address['province'] = None

            if 'distrito' in obj:
                try:
                    district = District.objects.get(name=obj['distrito'],
                                                    province=address['province'])
                    address['district'] = district
                except District.DoesNotExist:
                    address['district'] = None
            else:
                address['district'] = None

            if 'direccion' in obj:
                address['street'] = obj['direccion']
            else:
                address['street'] = ""

            if address:
                return AddressSerializer(address).data
            else:
                return None
        except Exception as e:
            print("error get_address")
            print(e)
            return None


    def get_business_name(self, obj):
        if 'nombre_o_razon_social' in obj:
            return obj['nombre_o_razon_social']
        else:
            return ""

    def get_status(self, obj):
        if 'estado_del_contribuyente' in obj:
            return obj['estado_del_contribuyente']
        else:
            return ""
