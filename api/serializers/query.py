"""Consultas."""
from rest_framework import serializers
from api.models import Specialist, Query, Message, Category, QueryPlansAcquired
from api.api_choices_models import ChoicesAPI as c
from django.utils.translation import ugettext_lazy as _
from api.utils.tools import get_time_message
from api.utils import querysets


# Serializer de Mensajes
class MessageSerializer(serializers.ModelSerializer):
    """Serializer para el mensaje."""

    msg_type = serializers.ChoiceField(choices=c.message_msg_type)
    # msg_type_name = serializers.SerializerMethodField()
    content_type = serializers.ChoiceField(choices=c.message_content_type)
    # content_type_name = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    room = serializers.CharField(max_length=100, required=False)

    class Meta:
        """Configuro el modelo y sus campos."""

        model = Message
        fields = ('id', 'message', 'msg_type', 'content_type',
                  'time', 'code', 'specialist', 'file_url', 'room')

        read_only_fields = ('id', 'time', 'code')

    def get_time(self, obj):
        """Devuelve el tiempo formateado en horas y minutos."""
        return str(obj.created_at.hour) + ':' + str(obj.created_at.minute)

    def get_msg_type_name(self, obj):
        """Devuelve el tipo de mensaje (answer,query,requery)."""
        return _(obj.get_msg_type_display())

    def get_content_type_name(self, obj):
        """Devuelve el tipo de contenido del mensaje (text,image,audio)."""
        return _(obj.get_content_type_display())

    def validate(self, data):
        """Validacion de Data."""
        required = _('required')
        if int(data["content_type"]) > 0 and data["file_url"] == '':
            raise serializers.ValidationError("file_url {}".format(required))
        if int(data["content_type"]) == 0 and data["message"] == '':
            raise serializers.ValidationError("text message {}".format(required))
        return data


class ListMessageSerializer(serializers.ModelSerializer):
    """Serializer para la representacion del mensaje."""

    class Meta:
        """Configuro el modelo y sus campos."""

        model = Message
        fields = ('id', 'message', 'msg_type', 'content_type',
                  'time', 'code', 'specialist', 'file_url', 'room')

    def to_representation(self, obj):
        """Redefinido nombres (claves) para firebase."""
        time = str(obj.created_at.hour) + ':' + str(obj.created_at.minute)
        return {"id": obj.id, "room": obj.room, "codeUser": obj.code, "fileType": obj.content_type,
                "fileUrl": obj.file_url, "message": obj.message, "messageType": obj.msg_type,
                "timeMessage": time, "read": obj.viewed}

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
    """serializador para devolver datos customizados de un diccionario dado."""

    fields = ('specialist_id', 'month_count', 'year_count')

    # establecemos que datos del diccionario pasado se mostrara en cada campo puesto en la tupla "Fields"
    def to_representation(self, dic):
        """Diccionario redefinido."""
        return {"specialist_id": dic['specialist_id'],
                "month_count": dic['month_count'], "year_count": dic['year_count']}


class QuerySerializer(serializers.ModelSerializer):
    """Serializer para crear consultas."""

    message = MessageSerializer(many=True)

    class Meta:
        """Meta."""

        model = Query
        fields = ('id', 'title', 'message', 'category', 'client')

    def validate(self, data):
        """Validaciones Generales."""
        # Valido si posee un plan activo
        if not querysets.has_active_plan(data["client"]):
            raise serializers.ValidationError(_("You need to have an active plan"))
        if not querysets.has_available_queries(data["client"]):
            raise serializers.ValidationError(_("You don't have available queries"))
        return data

    # def update(self, instance, validated_data):
    #     """Redefinido metodo actualizar."""
    #     # no se puede agregar msjs de ningun tipo una vez hah sido absuelta
    #     if int(instance.status) == 6 or int(instance.status) == 7:
    #         raise serializers.ValidationError(u"Query Absolved - can'not add more messages")
    #     data_message = validated_data.pop('message')
    #     specialist = Specialist.objects.get(pk=instance.specialist_id)
    #     data_message["specialist"] = specialist
    #     # se compara si el status fue respondida, entonces debemos declarar
    #     # que el tipo de mensaje es reconsulta, y que pasa a estatus 1,
    #     # (pendiente de declinar o responder por el especialista)
    #     if int(instance.status) == 4 or int(instance.status) == 5:
    #         data_message["msg_type"] = 'r'
    #         instance.status = 1
    #     Message.objects.create(query=instance, **data_message)
    #     instance.save()
    #     return instance

    def create(self, validated_data):
        """Redefinido metodo create."""
        # Buscamos el especialista principal de la especialidad dada
        specialist = Specialist.objects.get(type_specialist="m",
                                            category_id=validated_data["category"])
        data_messages = validated_data.pop('message')
        # Buscamos el plan activo y elegido
        acquired_plan = QueryPlansAcquired.objects.get(is_chosen=True, client=validated_data["client"])
        validated_data["specialist"] = specialist
        validated_data["status"] = 0
        validated_data["acquired_plan"] = acquired_plan
        # Creamos la consulta y sus mensajes
        query = Query.objects.create(**validated_data)
        # Recorremos los mensajes para crearlos todos
        for data_message in data_messages:
            # por defecto el tipo de mensaje al crearse debe de ser pregunta ('q')
            data_message["msg_type"] = "q"
            data_message["specialist"] = specialist
            # armamos la sala para el usuario
            data_message["room"] = 'u'+str(validated_data["client"].id)+'-'+'c'+str(validated_data["category"].id)
            data_message["code"] = validated_data["client"].code
            self.context['messages_data'] = data_message
            Message.objects.create(query=query, **data_message)
        # restamos una consulta disponible al plan adquirido
        acquired_plan.available_queries = acquired_plan.available_queries - 1
        acquired_plan.save()
        return query

    def to_representation(self, obj):
        """Redefinido metodo de representación del serializer."""
        ms = ListMessageSerializer(obj.message_set.all(), many=True).data
        chat = {}

        for message in ms:
            message["query"] = {"id": obj.id, "title": obj.title, "status": obj.status,
                                "calification": obj.calification}
            key_message = 'm'+str(message["id"])
            chat.update({key_message: dict(message)})

        return {'room': ms[0]["room"], "message": chat}


class QueryResponseSerializer(serializers.ModelSerializer):
    """Para respuesta de especialista."""

    message = MessageSerializer(write_only=True, many=True)

    class Meta:
        """Meta."""

        model = Query
        fields = ('id', 'message')

    def update(self, instance, validated_data):
        """Actualizar la consulta."""
        data_messages = validated_data.pop('message')
        self.context["size_msgs"] = len(data_messages)
        if instance.specialist.type_specialist == 'm':
            instance.status = 4
        else:
            instance.status = 5
        # Recorremos los mensajes para crearlos todos
        for data_message in data_messages:
            # por defecto el tipo de mensaje al crearse debe de ser pregunta ('q')
            data_message["msg_type"] = "a"
            data_message["specialist"] = self.context['specialist']
            # armamos la sala para el usuario
            data_message["room"] = 'u'+str(instance.client.id)+'-'+'c'+str(instance.category.id)
            # import pdb; pdb.set_trace()
            data_message["code"] = self.context['specialist'].code
            Message.objects.create(query=instance, **data_message)
        instance.save()
        return instance

    def to_representation(self, obj):
        """Redefinido metodo de representación del serializer."""
        size = self.context["size_msgs"]
        ms = ListMessageSerializer(obj.message_set.order_by('-created_at')[:size], many=True).data
        chat = {}

        for message in ms:
            message["query"] = {"id": obj.id, "title": obj.title, "status": obj.status,
                                "calification": obj.calification}
            key_message = 'm'+str(message["id"])
            chat.update({key_message: dict(message)})

        return {'room': ms[0]["room"], "message": chat}

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


# class ChatMessageFileSerializer(serializers.ModelSerializer):
#     """
#     Informacion de archivos para el chat de cliente
#     """
#
#     class Meta:
#         """declaracion del modelo y sus campos."""
#         model = MessageFile
#         fields = ('id','url_file', 'type_file')


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Informacion de los mensajes para chat de cliente
    """
    # file = serializers.SerializerMethodField()
    time_message = serializers.SerializerMethodField()
    query = serializers.SerializerMethodField()
    message_reference = serializers.SerializerMethodField()

    class Meta:
        """declaracion del modelo y sus campos."""
        model = Message
        fields = ('id', 'code', 'message', 'time_message', 'msg_type', 'viewed', 'content_type', 'file_url',
                 'query', 'message_reference')

    def get_time_message(self, obj):
        """Devuelve el tiempo cuando se realizo el mensaje del mensaje."""
        return get_time_message(obj['created_at'])

    def get_query(self, obj):
        """Objeto Query"""
        query = QueryChatClientSerializer(obj)
        return query.data


    def get_message_reference(self, obj):
        if obj['message_reference']:
            ref = Message.objects.get(pk = obj['message_reference'])
            message = ChatMessageReferenceSerializer(ref)
            return message.data

        return None


class ChatMessageReferenceSerializer(serializers.ModelSerializer):
    """
    Informacion de los mensajes para chat de cliente
    """
    class Meta:
        """declaracion del modelo y sus campos."""
        model = Message
        fields = ('id', 'message')

class QueryChatClientSerializer(serializers.ModelSerializer):
    """Serializer para listar consultas (Cliente)."""
    query_id = serializers.SerializerMethodField()

    class Meta:
        """Meta."""
        model = Query
        fields = ('title', 'category_id', 'calification', 'status', 'query_id')


    def get_query_id(self, obj):
        return obj['query_id']
