from rest_framework import serializers
from api.models import Client, LevelInstruction, Profession, Role, Countries
from api.models import CommercialGroup, EconomicSector



class ClientSerializer(serializers.ModelSerializer):
    level_instruction = serializers.SlugRelatedField(queryset=LevelInstruction.objects.all(), slug_field='name', allow_null=True)
    profession = serializers.SlugRelatedField(queryset=Profession.objects.all(), slug_field='name', allow_null=True)
    nationality = serializers.SlugRelatedField(queryset=Countries.objects.all(), slug_field='name')
    # role = serializers.SlugRelatedField(queryset=Role.objects.all(), slug_field='name')
    commercial_group = serializers.SlugRelatedField(queryset=CommercialGroup.objects.all(), slug_field='name', allow_null=True)
    economic_sector = serializers.SlugRelatedField(queryset=EconomicSector.objects.all(), slug_field='name', allow_null=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(allow_blank=False, write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        del data['confirm_password']
        return data

    def create(self, validated_data):
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
