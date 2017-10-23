from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from api.models import User, Client, LevelInstruction, Profession, Role, Countries
from api.models import CommercialGroup, EconomicSector, Address, Department
from api.models import Province, District, Category, Specialist, Query
from api.models import Parameter
from django.utils import six
import pdb
from datetime import datetime
from django.utils import timezone

class QuerySerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Query.option_status, read_only=True)
    last_time = serializers.SerializerMethodField()
    # media_files = FilesSerializer()

    class Meta:
        model = Query
        fields = ('id','title', 'message', 'status', 'last_time','category',
                 'client', 'specialist')
        read_only_fields = ('specialist','id','last_time')
    # Devuelvo la hora y minuto separados

    def get_last_time(self,obj):
        return str(obj.last_modified.date()) + ' ' + str(obj.last_modified.hour) + ':' + str(obj.last_modified.minute)

    # definir las validaciones correspondientes al crear una consulta
    def validate(self,data):
        # asignaremos el status 0 para la primera vez que sea creada
        data["has_precedent"] = False
        data["status"] = 0
        return data

    def create(self, validated_data):
        validated_data['specialist'] = Specialist.objects.get(type_specialist="m",
                                                              category_id = validated_data['category'])
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance
