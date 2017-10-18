from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from api.models import User, Client, LevelInstruction, Profession, Role, Countries
from api.models import CommercialGroup, EconomicSector, Address, Department

from api.models import Province, District, Category, Specialist, Query, Answer
from api.models import Parameter, Seller, Quota, Product, Purchase
from api.models import Province, District, Specialist, Query, Answer
from django.utils import six
import pdb
from datetime import datetime
from django.utils import timezone
import json

from django.db.models import Sum
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer que unicamente va ser utilizada para
    el servicio que devuelve todos los usuarios
    Este servicio es requerido por la web de administracion
    Unicamente expone el id y el nombre de usuario
    """
    class Meta:
        model = User
        fields = ('id', 'username')

class CommonValidation():

    def validate_img(self,photo):
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
        serializers.ChoiceField.__init__(self, choices,**kwargs)

    def to_representation(self, value):
        dictionary = dict(self.choices_to_dict)
        return dictionary.get(value)

class AddressSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ('street','department','department_name', 'province', 'province_name',
                  'district','district_name')

    def get_department_name(self,obj):
        return str(obj.department)

    def get_province_name(self,obj):
        return str(obj.province)

    def get_district_name(self,obj):
        return str(obj.district)

class ClientSerializer(serializers.ModelSerializer):
    # level_instruction = serializers.SlugRelatedField(queryset=LevelInstruction.objects.all(), slug_field='name', allow_null=True)
    level_instruction_name = serializers.SerializerMethodField()
    profession_name = serializers.SerializerMethodField()
    nationality_name = serializers.SerializerMethodField()
    commercial_group_name = serializers.SerializerMethodField()
    economic_sector_name = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    type_client = serializers.ChoiceField(choices=Client.options_type)
    sex = serializers.ChoiceField(choices=Client.options_sex, allow_blank=True)
    # sex_value = CustomChoiceField(choices=Client.options_sex)
    document_type = serializers.ChoiceField(choices=Client.options_documents)
    civil_state = serializers.ChoiceField(choices=Client.options_civil_state, allow_blank=True)
    ocupation = serializers.ChoiceField(choices=Client.options_ocupation, allow_blank=True)
    address = AddressSerializer()
    email_exact = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = Client
        fields = ('id', 'username', 'nick','type_client', 'first_name', 'last_name',
        'password', 'photo','sex','document_type', 'document_number','civil_state',
        'birthdate','address', 'ruc', 'email_exact', 'code', 'telephone', 'cellphone',
        'ciiu', 'activity_description', 'level_instruction','level_instruction_name',
        'business_name', 'agent_firstname','agent_lastname','position',
        'commercial_group', 'commercial_group_name','economic_sector',
        'economic_sector_name','institute', 'profession','profession_name',
        'ocupation', 'about', 'nationality','nationality_name')

    def get_level_instruction_name(self,obj):
        return str(obj.level_instruction)

    def get_profession_name(self,obj):
        return str(obj.profession)

    def get_nationality_name(self,obj):
        return str(obj.nationality)

    def get_commercial_group_name(self,obj):
        return str(obj.commercial_group)

    def get_economic_sector_name(self,obj):
        return str(obj.economic_sector)
    # Por si es necesario usarlo se usa el metodo
    # type_client = serializers.SerializerMethodField()
    # def get_type_client(self,obj):
    #     return obj.get_type_client_display()
    def validate_bussines_client(self,data):
        if 'business_name' not in data:
            raise serializers.ValidationError(u"Business name required.")
        if data['commercial_group'] == None:
            raise serializers.ValidationError(u"commercial_group must no be empty.")
        if data['economic_sector'] == None:
            raise serializers.ValidationError(u"economic_sector must no be empty.")
        if 'position' not in data:
            raise serializers.ValidationError(u"Position required.")
        if 'agent_firstname' not in data:
            raise serializers.ValidationError(u"agent_firstname required.")
        if 'agent_lastname' not in data:
            raise serializers.ValidationError(u"agent_lastname required.")
        return

    def validate(self, data):
        validation = CommonValidation()
        if 'photo' in data:
            validation.validate_img(photo=data['photo'])
        if data['type_client'] == 'b':
            self.validate_bussines_client(data)
        return data

    def create(self, validated_data):
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
    nationality_name = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    document_type = serializers.ChoiceField(choices=Specialist.options_documents)
    type_specialist = serializers.ChoiceField(choices=Specialist.options_type)
    address = AddressSerializer()
    email_exact = serializers.EmailField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Specialist
        fields = ('id', 'username', 'nick', 'first_name', 'last_name',
        'type_specialist','password', 'photo','document_type',
        'document_number','address', 'ruc', 'email_exact', 'code', 'telephone',
        'cellphone', 'business_name', 'payment_per_answer','cv','star_rating',
        'category','category_name','nationality','nationality_name')

    def get_nationality_name(self,obj):
        return str(obj.nationality)

    def get_category_name(self,obj):
        return str(obj.category)

    def validate(self,data):
        validation = CommonValidation()
        if 'photo' in data:
            validation.validate_img(photo=data['photo'])
        # Asegurarse que solo haya un especialista principal por categoria.
        if self.instance and self.instance.username != data["username"]:
            if data["type_specialist"] == "m" and Specialist.objects.filter(type_specialist="m",category__name=data["category"]).exists():
                raise serializers.ValidationError(u"Main specialist already exists.")
        return data

    def create(self, validated_data):
        data_address = validated_data.pop('address')
        address = Address.objects.create(**data_address)
        validated_data['address'] = address
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.nick = validated_data.get('nick', instance.nick)
        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.photo = validated_data.get('photo',instance.photo)
        instance.type_specialist = validated_data.get('type_specialist',instance.type_specialist)
        instance.document_type = validated_data.get('document_type',instance.document_type)
        instance.document_number = validated_data.get('document_number',instance.document_number)
        instance.email_exact = validated_data.get('email_exact',instance.email_exact)
        instance.telephone = validated_data.get('telephone',instance.telephone)
        instance.cellphone = validated_data.get('cellphone',instance.cellphone)
        instance.ruc = validated_data.get('ruc',instance.ruc)
        instance.business_name = validated_data.get('business_name',instance.business_name)
        instance.payment_per_answer = validated_data.get('payment_per_answer',instance.payment_per_answer)
        instance.category = validated_data.get('category',instance.category)
        data = validated_data
        if 'address' in validated_data:
            data_address = validated_data.pop('address')

            address = Address.objects.get(pk=instance.address_id)
            address.department = Department.objects.get(name=data_address["department"].name)
            address.province = Province.objects.get(name=data_address["province"].name)
            address.district = District.objects.get(name=data_address["district"].name)
            address.street = data_address['street']

            address.save()
            instance.address = address
        instance.save()
        return instance



class AnswerAccountSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    time_elapsed = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('id','date','time','specialist','created_at','time_elapsed')

    def get_date(self, obj):
        return obj.created_at.date()
    def get_time(self, obj):
        return str(obj.created_at.hour) + ':' + str(obj.created_at.minute)

    def get_time_elapsed(self, obj):
        # d.strftime("%Y-%m-%d %H:%M:%S")
        date_query = obj.query.created_at
        date_answer = obj.created_at
        diff = date_answer - date_query
        return str(diff)

class QueryAnswerSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    status = serializers.ChoiceField(choices=Query.option_status)
    answer = serializers.SerializerMethodField()
    is_delayed = serializers.SerializerMethodField()

    class Meta:
        model = Query
        fields = ('title','client','date','time','status','created_at','answer','is_delayed')

    def get_date(self,obj):
        return obj.created_at.date()

    # Devuelvo la hora y minuto separados
    def get_time(self,obj):
        return str(obj.created_at.hour) + ':' + str(obj.created_at.minute)

    def get_client(self,obj):
        return obj.client.nick
    # Devuelvo la respuesta relacionada a la consulta
    def get_answer(self,obj):
        answer_related = obj.answer_set.all()
        return AnswerAccountSerializer(answer_related,many=True).data

    # Verificar si el tiempo desde que se hizo la consulta fue superado al del
    # parametro y en base a eso determinar si esta con retraso o a tiempo
    def get_is_delayed(self,obj):
        date_query = obj.created_at
        time_delay = Parameter.objects.get(parameter="time_delay_response")
        try:
            answer =  obj.answer_set.get(pk=obj.id)
            date_elapsed = answer.created_at
        except:
            date_elapsed = timezone.now()
        diff = date_elapsed - date_query
        days = diff.days*24
        hours = diff.seconds // 3600
        if days >= int(time_delay.value) or hours >= int(time_delay.value):
            return True
        return False



# Serializer para consultar estado de cuenta del Especialista.
class SpecialistAccountSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(read_only=True,slug_field='name')
    query_answer = serializers.SerializerMethodField()
    photo_category = serializers.SerializerMethodField()

    class Meta:
        model = Specialist
        fields = ('id','first_name','last_name','code','nick','email_exact',
                  'photo','category','photo_category','payment_per_answer','query_answer')

        # No son campos editables ya que son de consulta solamente.
        read_only_fields = ('id','first_name','last_name','code','nick',
                            'email_exact','photo','category','photo_category',
                            'query_answer')

    # Traer por consulta relacionada
    def get_query_answer(self, obj):
        answer = obj.query_set.all()
        return QueryAnswerSerializer(answer,many=True).data

    def get_photo_category(self,obj):
        img = obj.category.image
        return img

class SellerSerializer(serializers.ModelSerializer):
    quota = serializers.SerializerMethodField()

    count_plans_seller = serializers.SerializerMethodField()
    count_queries = serializers.SerializerMethodField()

    address = AddressSerializer()

    class Meta:
        model   = Seller
        fields  = ('address','count_plans_seller','count_queries','quota','id','zone', 'username', 'nick', 'password', 'first_name',
        'last_name','email_exact', 'telephone','cellphone',
        'document_type','code', 'document_number', 'ruc')


        # No son campos editables ya que son de consulta solamente.
        read_only_fields = ('quota','id')


    def get_quota(self,obj):
        time_delay = Quota.objects.get(start__gte='2017-09-22',end__gte='2017-09-22')
        return time_delay.value

    def get_count_queries(self,obj):
        count = Product.objects.filter(purchases__isnull=False,purchases__seller=obj.id).aggregate(Sum('query_amount'))
        return count['query_amount__sum']

    def get_count_plans_seller(self,obj):
        count = Product.objects.filter(purchases__isnull=False,purchases__seller=obj.id).count()
        return count

    # def get_count_plans_seller(self,obj):
    #     time_delay = Quota.objects.get(start__gte='2017-09-22',end__gte='2017-09-22')
    #     return time_delay.value




class MediaSerializer(serializers.Serializer):
    photo = serializers.ImageField(
        max_length = None,
        required = False,
        allow_empty_file = False)
    filename = serializers.CharField()

    # class Meta:
    #     #model = Specialist
    #     fields = (
    #         'photo',
    #         'filename'
    #     )


