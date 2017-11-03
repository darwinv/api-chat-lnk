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

# Serializer de Mensajes
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

    # devolver los archivos adjuntos al msj
    def get_media_files(self,obj):
        medias = obj.messagefile_set.all()
        return MessageFileSerializer(medias,many=True).data

    def get_code_specialist(self, obj):
        return str(obj.specialist.code)

# Serializer para detalle de consulta
class QueryDetailSerializer(serializers.ModelSerializer):
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


# serializer para traer el ultimo mensaje de consulta, por detalle
# android especifico

# Serializer para crear consulta
class QueryCreateSerializer(serializers.ModelSerializer):
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
        validated_data["status"] = 0
        data_message["msg_type"] = "q"
        query = Query.objects.create(**validated_data)
        message = Message.objects.create(query=query,**data_message)
        return query

    # Si se llega a necesitar devolver personalizada la respuesta
    # redefinir este metodo y descomentarlo
    def to_representation(self, obj):
         message = MessageSerializer(obj.message_set.all().last()).data
         return {
            'id': obj.id,
            'title': obj.title,
            'msj': message
         }


# se utiliza para reconsulta, agregar mensajes nuevos a la consulta y respuesta
class QueryUpdateSerializer(serializers.ModelSerializer):
    # el message para este serializer
    # solo se puede escribir ya que drf no soporta la representacion
    # de writable nested relations,
    message = MessageSerializer(write_only=True)
    class Meta:
        model = Query
        fields = ('id','title','status','message','category','client')
        read_only_fields = ('status',)

    def update(self, instance, validated_data):
        # no se puede agregar msjs de ningun tipo una vez hah sido absuelta
        if int(instance.status) == 6 or int(instance.status) == 7:
            raise serializers.ValidationError(u"Query Absolved - can'not add more msgs")
        data_message = validated_data.pop('message')
        specialist = Specialist.objects.get(pk=instance.specialist_id)
        data_message["specialist"] = specialist
        # se compara si el status fue respondida, entonces debemos declarar
        # que el tipo de mensaje es reconsulta, y que pasa a estatus 1,
        # (pendiente de declinar o responder por el especialista)
        if int(instance.status) == 4 or int(instance.status) == 5:
            data_message["msg_type"] = 'r'
            instance.status = 1
        message = Message.objects.create(query=instance,**data_message)
        instance.save()
        return instance

# serializer para actualizar solo status de la consulta sin
# enviar msjs
class QueryUpdateStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Query.option_status)
    class Meta:
        model = Query
        fields = ('id','title','status','calification')
        read_only_fields = ('title',)

    def update(self, instance,validated_data):
        # se comprueba si hay un status
        if 'status' in validated_data:
            # si se quiere omitr la reconsulta, se debe garantizar que
            # la consulta fue respondida
            if int(validated_data["status"]) == 7:
                if int(instance.status) != 4 and int(instance.status) != 5:
                    raise serializers.ValidationError(u"to skip requery, it must be answered first.")

            instance.status = validated_data["status"]

        # se comprueba si hay calification en data
        # si se quiere calificar la respuesta debe estar absuelta primero
        if 'calification' in validated_data:
            if int(validated_data["calification"]) > 5:
                raise serializers.ValidationError(u"Invalid calification.")
            if int(instance.status) < 6:
                raise serializers.ValidationError(u"to qualify, it must be absolved first.")
            instance.calification = validated_data["calification"]
        instance.save()
        return instance



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
        msg =  obj.message_set.all().last()
        return msg.message
