from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from api.models import Client, LevelInstruction, Profession, Role, Countries
from api.models import CommercialGroup, EconomicSector, Address, Department
from api.models import Province, District, Category, Specialist
from django.utils import six
import pdb

class CommonValidation():

    # def match_passwords(self,password,confirm_password):
    #     if password != confirm_password:
    #         raise serializers.ValidationError(u"Passwords don't match")

    def validate_img(self,photo):
        extension = photo.split(".")[1]  # [0] returns path+filename
        valid_extensions = ['png', 'jpg', 'jpeg']
        if not extension.lower() in valid_extensions:
            raise serializers.ValidationError(u"Unsupported image extension.")



class CustomChoiceField(serializers.ChoiceField):
    def __init__(self, choices, **kwargs):
        self.choices_to_dict = choices
        serializers.ChoiceField.__init__(self, choices,**kwargs)

    def to_representation(self, value):
        # model = Client._meta
        dictionary = dict(self.choices_to_dict)
        return dictionary.get(value)

class AddressSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(queryset=Department.objects.all(), slug_field='name')
    province = serializers.SlugRelatedField(queryset=Province.objects.all(), slug_field='name')
    district = serializers.SlugRelatedField(queryset=District.objects.all(), slug_field='name')
    class Meta:
        model = Address
        fields = ('street','department', 'province', 'district')


class ClientSerializer(serializers.ModelSerializer):
    level_instruction = serializers.SlugRelatedField(queryset=LevelInstruction.objects.all(), slug_field='name', allow_null=True)
    profession = serializers.SlugRelatedField(queryset=Profession.objects.all(), slug_field='name', allow_null=True)
    nationality = serializers.SlugRelatedField(queryset=Countries.objects.all(), slug_field='name')
    commercial_group = serializers.SlugRelatedField(queryset=CommercialGroup.objects.all(), slug_field='name', allow_null=True)
    economic_sector = serializers.SlugRelatedField(queryset=EconomicSector.objects.all(), slug_field='name', allow_null=True)
    password = serializers.CharField(write_only=True)
    # confirm_password = serializers.CharField(allow_blank=False, write_only=True)
    type_client = CustomChoiceField(choices=Client.options_type)
    sex = CustomChoiceField(choices=Client.options_sex, allow_blank=True)
    document_type = CustomChoiceField(choices=Client.options_documents)
    civil_state = CustomChoiceField(choices=Client.options_civil_state, allow_blank=True)
    ocupation = CustomChoiceField(choices=Client.options_ocupation, allow_blank=True)
    address = AddressSerializer()
    email_exact = serializers.EmailField(validators=[UniqueValidator(queryset=Client.objects.all())])

    # Por si es necesario usarlo se usa el metodo
    # type_client = serializers.SerializerMethodField()
    # def get_type_client(self,obj):
    #     return obj.get_type_client_display()
    def validate_bussines_client(self,data):
        if 'bussiness_name' not in data:
            raise serializers.ValidationError(u"Bussiness name required.")
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
        validation.validate_img(photo=data['photo'])
        # validation.match_passwords(data['password'],data['confirm_password'])
        # del data['confirm_password']
        if data['type_client'] == 'b':
            self.validate_bussines_client(data)
        return data

    def create(self, validated_data):
        data_address = validated_data.pop('address')
        # address = AddressSerializer(data=data_address)
        address = Address.objects.create(**data_address)
        validated_data['address'] = address
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = Client
        fields = ('id', 'username', 'nick','type_client', 'first_name', 'last_name',
        'password', 'photo','sex','document_type', 'document_number',
        'civil_state','birthdate','address', 'ruc', 'email_exact', 'code',
        'telephone', 'cellphone', 'ciiu', 'activity_description', 'level_instruction',
        'bussiness_name', 'agent_firstname', 'agent_lastname', 'position',
        'commercial_group', 'economic_sector','institute', 'profession',
        'ocupation', 'about', 'nationality')

class SpecialistSerializer(serializers.ModelSerializer):
    nationality = serializers.SlugRelatedField(queryset=Countries.objects.all(), slug_field='name',required=False)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    # confirm_password = serializers.CharField(allow_blank=False, write_only=True)
    document_type = CustomChoiceField(choices=Specialist.options_documents)
    type_specialist = CustomChoiceField(choices=Specialist.options_type)
    address = AddressSerializer()
    email_exact = serializers.EmailField()
    category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='name')

    def validate(self,data):
        validation = CommonValidation()
        validation.validate_img(photo=data['photo'])
        # validation.match_passwords(data['password'],data['confirm_password'])
        if self.instance and self.instance.username != data["username"]:
            if data["type_specialist"] == "m" and Specialist.objects.filter(type_specialist="m",category__name=data["category"]).exists():
                raise serializers.ValidationError(u"Main specialist already exists.")
        return data

    def create(self, validated_data):
        data_address = validated_data.pop('address')
        # address = AddressSerializer(data=data_address)
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
        instance.bussiness_name = validated_data.get('bussiness_name',instance.bussiness_name)
        instance.payment_per_answer = validated_data.get('payment_per_answer',instance.payment_per_answer)
        instance.category = validated_data.get('category',instance.category)
        data = validated_data
        if 'address' in validated_data:
            data_address = validated_data.pop('address')
            address = Address.objects.get(pk=instance.id)
            address.department = Department.objects.get(name=data_address["department"].name)
            address.province = Province.objects.get(name=data_address["province"].name)
            address.district = District.objects.get(name=data_address["district"].name)
            address.street = data_address['street']
            address.save()
            instance.address = address
        instance.save()
        return instance

    class Meta:
        model = Specialist
        fields = ('id', 'username', 'nick', 'first_name', 'last_name',
        'type_specialist','password', 'photo','document_type',
        'document_number','address', 'ruc', 'email_exact', 'code', 'telephone',
        'cellphone', 'bussiness_name', 'payment_per_answer','cv','star_rating',
        'category','nationality')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'description')
