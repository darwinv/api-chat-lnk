"""Consultas."""
from rest_framework import serializers
from api.models import Specialist, Query, Message, Category
from api.models import MessageFile
from api.api_choices_models import ChoicesAPI as c
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, date, time, timedelta
from api.utils.tools import get_time_message


class MessageFileSerializer(serializers.ModelSerializer):
    """Serializer para los archivos en los mensajes."""

    type_file = serializers.ChoiceField(choices=c.messagefile_type_file)

    class Meta:
        """Agrego el modelo y sus campos."""

        model = MessageFile
        fields = ('url', 'type_file')


# Serializer de Mensajes
class MessageSerializer(serializers.ModelSerializer):
    """Serializer para el mensaje."""

    msg_type = serializers.ChoiceField(choices=c.message_msg_type)
    msg_type_name = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    media_files = serializers.SerializerMethodField()
    code_specialist = serializers.SerializerMethodField()

    class Meta:
        """Configuro el modelo y sus campos."""

        model = Message
        fields = ('id', 'message', 'msg_type', 'msg_type_name', 'time', 'media_files', 'code_specialist', 'specialist')

        read_only_fields = ('id', 'time', 'media_files', 'code_specialist')

    def get_time(self, obj):
        """Devuelve el tiempo formateado en horas y minutos."""
        return str(obj.created_at.hour) + ':' + str(obj.created_at.minute)

    # devolver los archivos adjuntos al msj
    def get_media_files(self, obj):
        """Devuelve los archivos de ese mensaje."""
        medias = obj.messagefile_set.all()
        return MessageFileSerializer(medias, many=True).data

    def get_code_specialist(self, obj):
        """Devuelve el codigo del especialista."""
        return str(obj.specialist.code)

    def get_msg_type_name(self, obj):
        """Devuelve el tipo de mensaje (answer,query,requery)."""
        return _(obj.get_msg_type_display())


# Serializer para detalle de consulta
class QueryDetailSerializer(serializers.ModelSerializer):
    """Serializer para el detalle de consulta."""

    messages = serializers.SerializerMethodField()
    code_client = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        """Agregado modelo y campos."""

        model = Query
        fields = (
            'id', 'title', 'status', 'messages', 'last_modified', 'client', 'code_client', 'specialist', 'category',
            'category_name', 'calification')
        read_only_fields = ('status', 'last_modified')

        # Traer por consulta relacionada

    def get_messages(self, obj):
        """Devuelve los mensajes."""
        message = obj.message_set.all()
        return MessageSerializer(message, many=True).data

    def get_code_client(self, obj):
        """Devuelve el codigo del cliente."""
        return str(obj.client.code)

    def get_category_name(self, obj):
        """Devuelve la especialidad de la consulta."""
        return _(str(obj.category))


# serializer para traer el ultimo mensaje de consulta, por detalle
# android especifico
class QueryDetailLastMsgSerializer(serializers.ModelSerializer):
    """Serializer para el ultimo msg de la consulta (especifico en android)."""

    last_msg = serializers.SerializerMethodField()
    code_client = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        """Agrego modelo y sus campos."""

        model = Query
        fields = (
            'id', 'title', 'status', 'last_msg', 'last_modified', 'client', 'code_client', 'specialist', 'category',
            'category_name', 'calification')
        read_only_fields = ('status', 'last_modified')

        # Traer por consulta relacionada

    def get_last_msg(self, obj):
        """Devuelve el ultimo mensaje."""
        msg = obj.message_set.all().last()
        return msg.message

    def get_code_client(self, obj):
        """Devuelve el codigo del cliente."""
        return str(obj.client.code)

    def get_category_name(self, obj):
        """Devuelve el nombre de la especialidad."""
        return _(str(obj.category))

class QueryCustomSerializer(serializers.Serializer):
    #serializador para devolver datos customizados de un diccionario dado
    fields = ('specialist_id','month_count','year_count')

    #establecemos que datos del diccionario pasado se mostrara en cada campo puesto en la tupla "Fields"
    def to_representation(self, dic):
        return {"specialist_id": dic['specialist_id'],"month_count": dic['month_count'],"year_count": dic['year_count']}

class QuerySerializer(serializers.ModelSerializer):
    """Serializer para crear consultas."""

    # el message para este serializer
    # solo se puede escribir ya que drf no soporta la representacion
    # de writable nested relations,
    message = MessageSerializer(write_only=True)

    class Meta:
        """Meta."""

        model = Query
        fields = ('id', 'title', 'message', 'category', 'client')

    def update(self, instance, validated_data):
        """Redefinido metodo actualizar."""
        # no se puede agregar msjs de ningun tipo una vez hah sido absuelta
        if int(instance.status) == 6 or int(instance.status) == 7:
            raise serializers.ValidationError(u"Query Absolved - can'not add more messages")
        data_message = validated_data.pop('message')
        specialist = Specialist.objects.get(pk=instance.specialist_id)
        data_message["specialist"] = specialist
        # se compara si el status fue respondida, entonces debemos declarar
        # que el tipo de mensaje es reconsulta, y que pasa a estatus 1,
        # (pendiente de declinar o responder por el especialista)
        if int(instance.status) == 4 or int(instance.status) == 5:
            data_message["msg_type"] = 'r'
            instance.status = 1
        Message.objects.create(query=instance, **data_message)
        instance.save()
        return instance

    def create(self, validated_data):
        """Redefinido metodo create."""
        validated_data["specialist"] = Specialist.objects.get(type_specialist="m",
                                                              category_id=validated_data["category"])
        data_message = validated_data.pop('message')
        validated_data["status"] = 0
        data_message["msg_type"] = "q"
        query = Query.objects.create(**validated_data)
        Message.objects.create(query=query, **data_message)
        return query

    # Si se llega a necesitar devolver personalizada la respuesta
    # redefinir este metodo y descomentarlo
    def to_representation(self, obj):
        """Redefinido metodo de representación del serializer."""
        ms = MessageSerializer(obj.message_set.all().order_by('-created_at')[:1], many=True).data
        # message = MessageSerializer(obj.message_set.all().last()).data
        return {'id': obj.id, 'title': obj.title, 'status': obj.status, 'messages': ms,
                'last_modified': obj.last_modified, 'client': obj.client_id, 'code_client': str(obj.client.code),
                'specialist': obj.specialist_id, 'category': obj.category_id, 'category_name': _(str(obj.category)),
                'calification': obj.calification}


# se utiliza para reconsulta, agregar mensajes nuevos a la consulta y respuesta
# class QueryUpdateSerializer(serializers.ModelSerializer):
#     # el message para este serializer
#     # solo se puede escribir ya que drf no soporta la representacion
#     # de writable nested relations,
#     message = MessageSerializer(write_only=True)
#     class Meta:
#         model = Query
#         fields = ('id','title','status','message','category','client')
#         read_only_fields = ('status',)
#
#     def update(self, instance, validated_data):
#         # no se puede agregar msjs de ningun tipo una vez hah sido absuelta
#         if int(instance.status) == 6 or int(instance.status) == 7:
#             raise serializers.ValidationError(u"Query Absolved - can'not add more msgs")
#         data_message = validated_data.pop('message')
#         specialist = Specialist.objects.get(pk=instance.specialist_id)
#         data_message["specialist"] = specialist
#         # se compara si el status fue respondida, entonces debemos declarar
#         # que el tipo de mensaje es reconsulta, y que pasa a estatus 1,
#         # (pendiente de declinar o responder por el especialista)
#         if int(instance.status) == 4 or int(instance.status) == 5:
#             data_message["msg_type"] = 'r'
#             instance.status = 1
#         message = Message.objects.create(query=instance,**data_message)
#         instance.save()
#         return instance

# serializer para actualizar solo status de la consulta sin
# enviar msjs
class QueryUpdateStatusSerializer(serializers.ModelSerializer):
    """Serializer para actualizar los estatus de las consultas."""

    status = serializers.ChoiceField(choices=c.query_status)

    class Meta:
        """Meta."""

        model = Query
        fields = ('id', 'title', 'status', 'calification')
        read_only_fields = ('title',)

    def update(self, instance, validated_data):
        """Redefinido metodo actualizar."""
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

    def to_representation(self, obj):
        """Redefinido metodo de representación."""
        return {"calification": obj.calification, "status": obj.status}


class QueryListClientSerializer(serializers.ModelSerializer):
    """Serializer para listar consultas (Cliente)."""

    name = serializers.SerializerMethodField()
    status_message = serializers.SerializerMethodField()
    time_message = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Category
        fields = ('id', 'name', 'image', 'description', 'status_message', 'time_message')

    def get_name(self, obj):
        """Devuelve el nombre de la especialidad."""
        return _(obj.name)

    def get_status_message(self, obj):
        """Devuelve si fue visto el ultimo mensaje."""
        user = self.context['user']
        try:
            status = Query.objects.filter(category_id=obj.id, client_id=user.id)\
                   .values('message__viewed').latest('message__created_at')
            return status['message__viewed']
        except Query.DoesNotExist:
            return None

    def get_time_message(self, obj):
        """Devuelve el tiempo del mensaje."""
        user = self.context['user']
        try:
            query = Query.objects.filter(category_id=obj.id, client_id=user.id)\
                             .values('message__created_at').latest('message__created_at')

            return get_time_message(query['message__created_at'])
            
        except Query.DoesNotExist:
            return None


class QueryListSpecialistSerializer(serializers.ModelSerializer):
    """Serializer para listar consultas (Especialista)."""

    status = serializers.ChoiceField(choices=c.query_status, read_only=True)
    last_modified = serializers.SerializerMethodField()
    # media_files = FilesSerializer()
    last_msg = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Query
        fields = (
            'id', 'title', 'last_msg', 'status', 'last_modified', 'category', 'category_name', 'client', 'specialist',
            'calification')
        read_only_fields = ('specialist', 'id', 'last_time')

    # Devuelvo la hora y minuto separados
    def get_last_modified(self, obj):
        """Devuelve la fecha y hora de la ultima modificación."""
        return str(obj.last_modified.date()) + ' ' + str(obj.last_modified.hour) + ':' + str(obj.last_modified.minute)

    def get_category_name(self, obj):
        """Devuelve la especialidad."""
        return _(str(obj.category))

    def get_last_msg(self, obj):
        """Devuelve el ultimo mensaje de la consulta."""
        msg = obj.message_set.all().last()
        return msg.message


class ChatMessageFileSerializer(serializers.ModelSerializer):
    """
    Informacion de archivos para el chat de cliente
    """

    class Meta:
        """declaracion del modelo y sus campos."""
        model = MessageFile
        fields = ('id','url_file', 'type_file')


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Informacion de los mensajes para chat de cliente
    """
    file = serializers.SerializerMethodField()
    time_message = serializers.SerializerMethodField()

    class Meta:
        """declaracion del modelo y sus campos."""
        model = Message
        fields = ('id','nick', 'code', 'message', 'time_message', 'msg_type', 'viewed', 'file')

    def get_file(self, obj):
        msg = MessageFile.objects.filter(message=obj['id']).all()
        data = ChatMessageFileSerializer(msg, many=True)
        return data.data

    def get_time_message(self, obj):
        """Devuelve el tiempo cuando se realizo el mensaje del mensaje."""
        return get_time_message(obj['created_at'])


class QueryChatClientSerializer(serializers.ModelSerializer):
    """Serializer para listar consultas (Cliente)."""
    id = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        """Meta."""
        model = Query
        fields = ('title', 'category_id', 'calification', 'status', 'message','id')

    def get_id(self, obj):
        return obj['query_id']

    def get_message(self, obj):
        message = ChatMessageSerializer(obj)
        return message.data

    
