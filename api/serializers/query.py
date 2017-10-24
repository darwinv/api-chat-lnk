from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from api.models import User, Client, LevelInstruction, Profession, Role, Countries
from api.models import CommercialGroup, EconomicSector, Address, Department
from api.models import Province, District, Category, Specialist, Query, Message
from api.models import Parameter, MessageFile
from django.utils import six
import pdb
from datetime import datetime
from django.utils import timezone


class MessageFileSerializer(serializers.ModelSerializer):
    type_file = serializers.ChoiceField(choices=MessageFile.options_type_file)
    class Meta:
        model = MessageFile
        fields = ('url','type_file')

class MessageSerializer(serializers.ModelSerializer):
    msg_type = serializers.ChoiceField(choices=Message.options_msg_type)
    time = serializers.SerializerMethodField()
    media_files = serializers.SerializerMethodField()
    code_specialist = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id','message','msg_type','time',
                 'media_files','code_specialist','specialist')

        read_only_fields = ('id','time','media_files','code_specialist')

    def get_time(self,obj):
        return str(obj.created_at.hour) + ':' + str(obj.created_at.minute)

    def get_media_files(self,obj):
        medias = obj.messagefile_set.all()
        return MessageFileSerializer(medias,many=True).data

    def get_code_specialist(self, obj):
        return str(obj.specialist.code)

class QuerySerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    code_client = serializers.SerializerMethodField()

    class Meta:
        model = Query
        fields = ('title','status','messages','last_modified',
                  'client','code_client','specialist', 'category')
        read_only_fields = ('status','last_modified')

        # Traer por consulta relacionada
    def get_messages(self, obj):
        message = obj.message_set.all()
        return MessageSerializer(message,many=True).data

    def get_code_client(self,obj):
        return str(obj.client.code)

class QueryCreateUpdateSerializer(serializers.ModelSerializer):
    # el message para este serializer
    # solo se puede escribir ya que drf no soporta la representacion
    # de writable nested relations,
    message = MessageSerializer(write_only=True)

    class Meta:
        model = Query
        fields = ('id','title','message','category','client')

    def create(self, validated_data):
        validated_data["specialist"] = Specialist.objects.get(type_specialist="m",
                                                        category_id=validated_data["category"])
        data_message = validated_data.pop('message')
        query = Query.objects.create(**validated_data)
        message = Message.objects.create(query=query,**data_message)
        return query

    # Si se llega a necesitar devolver personalizada la respuesta
    # redefinir este metodo y descomentarlo
    #  def to_representation(self, obj):
    #     return {
    #         'title': obj.title,
    #         'msj': obj.get_message
    #     }


class QueryListSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Query.option_status, read_only=True)
    last_modified = serializers.SerializerMethodField()
    # media_files = FilesSerializer()
    last_msg = serializers.SerializerMethodField()

    class Meta:
        model = Query
        fields = ('id','title','last_msg','status', 'last_modified','category',
                 'client','specialist')
        read_only_fields = ('specialist','id','last_time')

    # Devuelvo la hora y minuto separados
    def get_last_modified(self,obj):
        return str(obj.last_modified.date()) + ' ' + str(obj.last_modified.hour) + ':' + str(obj.last_modified.minute)

    def get_last_msg(self, obj):
        # pdb.set_trace()
        msg =  obj.message_set.all().last()
        return msg.message
    #
    # # definir las validaciones correspondientes al crear una consulta
    # def validate(self,data):
    #     # asignaremos el status 0 para la primera vez que sea creada
    #     data["has_precedent"] = False
    #     data["status"] = 0
    #     return data
    #
    # def create(self, validated_data):
    #     validated_data['specialist'] = Specialist.objects.get(type_specialist="m",
    #                                                           category_id = validated_data['category'])
    #     instance = self.Meta.model(**validated_data)
    #     instance.save()
    #     return instance
