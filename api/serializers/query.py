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

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('message')



class QuerySerializer(serializers.ModelSerializer):
    messages = MessageSerializer()

    class Meta:
        model = Query
        fields = ('title','status','messages','last_modified',
                  'client', 'specialist', 'category')

        read_only_fields = ('status','last_modified')


class QueryListSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Query.option_status, read_only=True)
    last_time = serializers.SerializerMethodField()
    # media_files = FilesSerializer()
    last_msg = serializers.SerializerMethodField()

    class Meta:
        model = Query
        fields = ('id','title','last_msg','status', 'last_time','category',
                 'client', 'specialist')
        read_only_fields = ('specialist','id','last_time')
    # Devuelvo la hora y minuto separados

    def get_last_time(self,obj):
        return str(obj.last_modified.date()) + ' ' + str(obj.last_modified.hour) + ':' + str(obj.last_modified.minute)

    def get_last_msg(self, obj):
        # pdb.set_trace()
        msg =  obj.message_set.all().last()
        return msg.message
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
