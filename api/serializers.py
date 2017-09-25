from rest_framework import serializers
from api.models import Client, LevelInstruction, Profession, Role, Countries
from api.models import CommercialGroup, EconomicSector, Address, Department
from api.models import Province, District, Category
from django.utils import six

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
    # role = serializers.SlugRelatedField(queryset=Role.objects.all(), slug_field='name')
    commercial_group = serializers.SlugRelatedField(queryset=CommercialGroup.objects.all(), slug_field='name', allow_null=True)
    economic_sector = serializers.SlugRelatedField(queryset=EconomicSector.objects.all(), slug_field='name', allow_null=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(allow_blank=False, write_only=True)
    type_client = CustomChoiceField(choices=Client.options_type)
    sex = CustomChoiceField(choices=Client.options_sex, allow_blank=True)
    document_type = CustomChoiceField(choices=Client.options_documents)
    civil_state = CustomChoiceField(choices=Client.options_civil_state, allow_blank=True)
    ocupation = CustomChoiceField(choices=Client.options_ocupation, allow_blank=True)
    address = AddressSerializer()
    email_exact = serializers.EmailField()

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
        extension = data['photo'].split(".")[1]  # [0] returns path+filename
        valid_extensions = ['png', 'jpg', 'jpeg']

        if not extension.lower() in valid_extensions:
             raise serializers.ValidationError(u"Unsupported image extension.")
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(u"Passwords don't match")
        del data['confirm_password']

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
        'password','confirm_password', 'photo','sex','document_type', 'document_number',
        'civil_state','birthdate','address', 'ruc', 'email_exact', 'code',
        'telephone', 'cellphone', 'ciiu', 'activity_description', 'level_instruction',
        'bussiness_name', 'agent_firstname', 'agent_lastname', 'position',
        'commercial_group', 'economic_sector','institute', 'profession',
        'ocupation', 'about', 'nationality')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'description')
