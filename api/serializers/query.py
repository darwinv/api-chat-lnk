"""Consultas."""
from django.utils.translation import ugettext_lazy as _
from django.db.models import Avg
from rest_framework import serializers
from api.models import Specialist, Query, Message, Category, QueryPlansAcquired
from api.models import User, GroupMessage, Declinator
from api.api_choices_models import ChoicesAPI as c
from api.utils import querysets
from api.utils.parameters import Params
from api.utils.functions import generate_message_code_user
from api import pyrebase
import sys


# Serializer de Mensajes
class MessageSerializer(serializers.ModelSerializer):
    """Serializer para el mensaje."""

    msg_type = serializers.ChoiceField(choices=c.message_msg_type)
    # msg_type_name = serializers.SerializerMethodField()
    content_type = serializers.ChoiceField(choices=c.message_content_type)
    # content_type_name = serializers.SerializerMethodField()
    # time = serializers.SerializerMethodField()
    room = serializers.CharField(max_length=100, required=False)
    created_at = serializers.SerializerMethodField()

    class Meta:
        """Configuro el modelo y sus campos."""

        model = Message
        fields = ('id', 'message', 'msg_type', 'content_type',
                  'message_reference', 'created_at', 'code',
                  'specialist', 'file_url', 'room', 'uploaded',
                  'file_preview_url')

        read_only_fields = ('id', 'created_at', 'code')

    # def get_time(self, obj):
    #     """Devuelve el tiempo formateado en horas y minutos."""
    #     return str(obj.created_at.hour) + ':' + str(obj.created_at.minute)

    def get_created_at(self, obj):
        return str(obj.created_at)

    def get_msg_type_name(self, obj):
        """Devuelve el tipo de mensaje (answer,query,requery)."""
        return _(obj.get_msg_type_display())

    def get_content_type_name(self, obj):
        """Devuelve el tipo de contenido del mensaje (text,image,audio)."""
        return _(obj.get_content_type_display())

    def validate(self, data):
        """Validacion de Data."""
        required = _('required')
        if int(data["content_type"]) > 1 and data["file_url"] == '':
            raise serializers.ValidationError({"file_url": [required]})
        if int(data["content_type"]) == 1 and data["message"] == '':
            raise serializers.ValidationError({"message": [required]})
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
        time = str(obj.created_at)
        user_id = obj.query.client.id
        reference_id = 0
        if obj.specialist:
            user_id = obj.specialist.id
        # metodo para renderizar objeto en el json
        if obj.message_reference:
            reference_id = obj.message_reference.id
        return {"id": obj.id, "room": obj.room, "codeUser": obj.code,
                "fileType": obj.content_type, "fileUrl": obj.file_url,
                "filePreviewUrl": obj.file_preview_url,
                "message": obj.message, "messageType": obj.msg_type,
                "messageReference": reference_id,
                "groupStatus": obj.group.status, "groupId": obj.group.id,
                "timeMessage": time, "user_id": user_id
                }

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
            'category_name', 'qualification')
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
            'category_name', 'qualification')
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

    # establecemos que datos del diccionario pasado se mostrara en cada
    # campo puesto en la tupla "Fields"
    def to_representation(self, dic):
        """Diccionario redefinido."""
        return {"specialist_id": dic['specialist_id'],
                "month_count": dic['month_count'], "year_count": dic['year_count']}


# Serializer solo para crear.
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

        if not querysets.has_active_plan(data["client"].id):
            raise serializers.ValidationError(_("You need to have an active plan"))
        if not querysets.has_available_queries(data["client"].id):
            raise serializers.ValidationError(_("You don't have available queries"))
        return data

    def create(self, validated_data):
        """Redefinido metodo create."""
        # Buscamos el especialista principal de la especialidad dada
        specialist = Specialist.objects.get(
            type_specialist="m", category_id=validated_data["category"])
        data_messages = validated_data.pop('message')
        # Buscamos el plan activo y elegido

        acq_plan = QueryPlansAcquired.objects.get(
                            queryplansclient__is_chosen=True, queryplansclient__client=validated_data["client"])
        validated_data["specialist"] = specialist
        validated_data["status"] = 1
        validated_data["acquired_plan"] = acq_plan
        # Creamos la consulta y sus mensajes
        validated_data["available_requeries"] = acq_plan.available_requeries
        query = Query.objects.create(**validated_data)
        # creamos el grupo para ese mensaje
        group = GroupMessage.objects.create(status=1)
        # Generar codigo de usuario para chat
        code_user = generate_message_code_user(validated_data["client"], acq_plan)
        # Recorremos los mensajes para crearlos todos
        for data_message in data_messages:
            # por defecto el tipo de mensaje al crearse
            # debe de ser pregunta ('q')
            data_message["msg_type"] = "q"
            # data_message["specialist"] = specialist
            # armamos la sala para el usuario
            data_message["room"] = Params.PREFIX['client']+str(
                validated_data["client"].id)+'-'+Params.PREFIX['category']+str(
                    validated_data["category"].id)
            # data_message["code"] = validated_data["client"].code
            data_message["code"] = code_user
            # self.context["user_id"] = validated_data["client"].id
            Message.objects.create(query=query, group=group, **data_message)
        # restamos una consulta disponible al plan adquirido
        acq_plan.available_queries = acq_plan.available_queries - 1
        # si el plan queda en 0 consultas, pasa a culminado
        if acq_plan.available_queries == 0 and acq_plan.queries_to_pay == 0:
            acq_plan.status = 5
        acq_plan.save()
        if 'test' not in sys.argv:
            pyrebase.chosen_plan(
                validated_data["client"].id,
                {"available_queries": acq_plan.available_queries})
        return query

    def to_representation(self, obj):
        """Redefinido metodo de representación del serializer."""
        ms = ListMessageSerializer(obj.message_set.all(), many=True).data
        chat = {}
        messages_files = []
        for message in ms:
            if int(message['fileType']) > 1:
                message['uploaded'] = 1
                messages_files.append(message["id"])
            else:
                message['uploaded'] = 2
            av_reqs = obj.available_requeries
            message["query_id"] = obj.id

            key_message = Params.PREFIX['message']+str(message["id"])
            chat.update({key_message: dict(message)})

        # devuelvo el objeto query para actualizar en su nodo de firebase
        obj_query = {"id": obj.id, "title": obj.title, "status": obj.status,
                     "qualification": obj.qualification,
                     "availableRequeries": av_reqs,
                     "specialist_id": obj.specialist.id}

        return {'room': ms[0]["room"], "message": chat,
                "message_files_id": messages_files, 'status': obj.status,
                "category": obj.category.id, "query_id": obj.id,
                "obj_query": obj_query}


class BaseQueryResponseSerializer(serializers.ModelSerializer):
    """Para base de respuesta y reconsulta."""

    message = MessageSerializer(many=True)

    def to_representation(self, obj):
        """Redefinido metodo de representación del serializer."""
        size = self.context["size_msgs"]
        ms = ListMessageSerializer(
            obj.message_set.order_by('-created_at')[:size], many=True).data
        chat = {}
        messages_files = []
        for message in ms:
            if int(message['fileType']) > 1:
                message['uploaded'] = 1
                messages_files.append(message["id"])
            else:
                message['uploaded'] = 2

            av_reqs = obj.available_requeries
            message["query_id"] = obj.id
            key_message = Params.PREFIX['message']+str(message["id"])
            chat.update({key_message: dict(message)})

        obj_query = {"id": obj.id, "title": obj.title, "status": obj.status,
                     "qualification": obj.qualification,
                     "availableRequeries": av_reqs,
                     "specialist_id": obj.specialist.id}

        return {'room': ms[0]["room"], "message": chat,
                "message_files_id": messages_files,
                "category": obj.category.id, 'status': obj.status,
                "query_id": obj.id, "client_id": obj.client.id,
                "specialist_id": obj.specialist.id, "obj_query": obj_query}


class QueryResponseSerializer(BaseQueryResponseSerializer):
    """Para respuesta de especialista."""

    message = MessageSerializer(many=True)

    class Meta:
        """Meta."""

        model = Query
        fields = ('id', 'message')

    def update(self, instance, validated_data):
        """Actualizar la consulta."""
        data_messages = validated_data.pop('message')
        self.context["size_msgs"] = len(data_messages)
        # Recorremos los mensajes para crearlos todos
        group = GroupMessage.objects.create(status=1)
        for data_message in data_messages:
            # por defecto el tipo de mensaje al actualizarse debe
            # de ser pregunta ('a')
            data_message["msg_type"] = "a"
            data_message["specialist"] = self.context['specialist']
            # armamos la sala para el usuario
            data_message["room"] = Params.PREFIX['client'] +\
                str(instance.client.id)+'-'+Params.PREFIX['category'] +\
                str(instance.category.id)
            data_message["code"] = self.context['specialist'].code
            # se busca el mensaje de referencia y se extrae de la respuesta
            if data_message['message_reference'] is not None and data_message['message_reference'] != 0:
                ms_ref = data_message['message_reference'].id
            Message.objects.create(query=instance, group=group, **data_message)


        # Actualizo status dependiendo de cantidad de reconsultas
        if instance.available_requeries >= 1:
            instance.status = 3
        else:
            instance.status = 4
        # actualizo el estado del grupo al cual se le responde
        gp = GroupMessage.objects.get(message__id=ms_ref)
        gp.status = 2
        # se pasa el queryset
        # pyrebase.update_status_group_messages(msgs, gp.status)
        gp.save()
        instance.save()
        return instance


class ReQuerySerializer(BaseQueryResponseSerializer):
    """Serializer de Reconsulta."""

    class Meta:
        """Meta."""

        model = Query
        fields = ('id', 'message')

    def update(self, instance, validated_data):
        """Update."""
        if instance.available_requeries == 0:
            raise serializers.ValidationError(
                {"non_field_errors": _("You don't have available requeries")})

        data_messages = validated_data.pop('message')
        self.context["size_msgs"] = len(data_messages)
        # creamos el grupo
        group = GroupMessage.objects.create(status=1)
        # Generar codigo de usuario para chat
        code_user = generate_message_code_user(instance.client,
                                                 instance.acquired_plan)
        # Recorremos los mensajes para crearlos todos
        for data_message in data_messages:
            # por defecto el tipo de mensaje al actualizarse debe
            # de ser re consulta ('r')
            data_message["msg_type"] = "r"
            # armamos la sala para el usuario
            data_message["room"] = Params.PREFIX['client'] +\
                str(instance.client.id)+'-'+Params.PREFIX['category'] +\
                str(instance.category.id)

            # se busca el mensaje de referencia y se extrae de la respuesta
            if 'message_reference' in data_message and data_message['message_reference'] != 0:
                ms_ref = data_message['message_reference'].id
            Message.objects.create(query=instance, group=group, **data_message)
        instance.status = 2  # actualizo status
        # actualizo el estado del grupo al cual se le responde
        gp = GroupMessage.objects.get(message__id=ms_ref)
        gp.status = 2
        # se pasa el queryset
        gp.save()
        av_requeries = instance.available_requeries - 1
        instance.available_requeries = av_requeries
        instance.save()
        return instance



# serializer para actualizar solo status de la consulta sin
# enviar msjs
class QueryUpdateStatusSerializer(serializers.ModelSerializer):
    """Serializer para actualizar los estatus de las consultas."""

    status = serializers.ChoiceField(choices=c.query_status)

    class Meta:
        """Meta."""

        model = Query
        fields = ('id', 'title', 'status', 'qualification')
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

        # se comprueba si hay qualification en data
        # si se quiere calificar la respuesta debe estar absuelta primero
        if 'qualification' in validated_data:
            if int(validated_data["qualification"]) > 5:
                raise serializers.ValidationError(u"Invalid qualification.")
            if int(instance.status) < 6:
                raise serializers.ValidationError(u"to qualify, it must be absolved first.")
            instance.qualification = validated_data["qualification"]
        instance.save()
        return instance

    def to_representation(self, obj):
        """Redefinido metodo de representación."""
        return {"qualification": obj.qualification, "status": obj.status}


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
            return query['message__created_at']

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
            'qualification')
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
    """Informacion de los mensajes para chat de cliente."""

    time_message = serializers.SerializerMethodField()
    query = serializers.SerializerMethodField()
    message_reference = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        """declaracion del modelo y sus campos."""

        model = Message
        fields = ('id', 'code', 'message', 'time_message', 'msg_type', 'viewed', 'content_type', 'file_url',
                  'query', 'message_reference', 'user_id')

    def get_time_message(self, obj):
        """Devuelve el tiempo cuando se realizo el mensaje del mensaje."""
        return obj['created_at']

    def get_query(self, obj):
        """Objeto Query."""
        query = QueryChatClientSerializer(obj)
        return query.data

    def get_user_id(self, obj):
        """Devolver id del usuario que lo envia."""

        if obj["specialist_id"]:
            return obj["specialist_id"]
        return obj["query__client_id"]

    def get_message_reference(self, obj):
        if obj['message_reference']:
            ref = Message.objects.get(pk=obj['message_reference'])
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
        fields = ('title', 'category_id', 'qualification', 'status', 'query_id')


    def get_query_id(self, obj):
        return obj['query_id']

class QueryMessageSerializer(serializers.ModelSerializer):
    """Informacion de los mensajes para chat de cliente."""

    message = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        """Meta."""
        model = Query
        fields = ('id', 'title', 'message', 'user')

    def get_message(self, obj):
        """Objeto Message."""
        message = Message.objects.filter(query=obj['id'])
        serializer = MessageSerializer(message, many=True)
        return serializer.data

    def get_user(self, obj):
        """Objeto Message."""
        serializer = UserQueryMessageSerializer(obj, partial=True)
        return serializer.data

class UserQueryMessageSerializer(serializers.ModelSerializer):
    """User """
    display_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        """Meta."""
        model = User
        fields = ('display_name', 'photo')

    def get_display_name(self, obj):
        """String Displayname."""

        if obj['client__nick'] and obj['client__nick'] != "":
            display_name = obj['client__nick']
        else:
            display_name = "{} {}".format(obj['client__first_name'], obj['client__last_name'])

        return display_name

    def get_photo(self, obj):
        """String Photo."""
        return obj['client__photo']

class QueryAcceptSerializer(serializers.ModelSerializer):
    """Cambiar clave de usuario."""

    class Meta:
        """Meta."""
        model = Query
        fields = ('status',)

    def update(self, instance, validated_data):
        """Redefinir update."""
        instance.status = validated_data["status"]
        instance.save()
        return instance


class QueryDeriveSerializer(serializers.ModelSerializer):
    """Cambiar clave de usuario."""

    class Meta:
        """Meta."""
        model = Query
        fields = ('status', 'specialist')

    def update(self, instance, validated_data):
        """Redefinir update."""
        instance.status = validated_data["status"]
        instance.specialist = validated_data["specialist"]
        instance.save()
        return instance


class QueryQualifySerializer(serializers.ModelSerializer):
    """Calificar Consulta."""

    qualification = serializers.IntegerField(max_value=5, min_value=1)

    class Meta:
        """Meta."""
        model = Query
        fields = ('status', 'qualification')
        read_only_fields = ('status',)

    def update(self, instance, validated_data):
        """Redefinir update."""
        instance.status = 5
        instance.qualification = validated_data["qualification"]
        instance.save()
        rating = Query.objects.filter(
            specialist=instance.specialist).aggregate(Avg('qualification'))
        Specialist.objects.filter(
            pk=instance.specialist).update(
                star_rating=int(rating["qualification__avg"]))
        return instance


class QueryDeclineSerializer(QueryDeriveSerializer):
    """Cambiar clave de usuario."""

    name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        """Meta."""
        model = Declinator
        fields = ('message', 'name', 'last_name')

    def update(self, instance, validated_data):
        validated_data['status'] = self.context['status']
        validated_data['specialist'] = self.context['specialist']
        super(QueryDeclineSerializer, self).update(instance, validated_data)

        data_declinator = {}
        data_declinator["message"] = validated_data['message']
        data_declinator["query"] = instance
        specialist = self.context['specialist_declined']
        data_declinator["specialist"] = Specialist.objects.get(pk=specialist)
        return Declinator.objects.create(**data_declinator)

    def get_name(self, obj):
        if type(obj) is dict and 'specialist__first_name' in obj:
            return obj['specialist__first_name']
        return ""


    def get_last_name(self, obj):
        if type(obj) is dict and 'specialist__last_name' in obj:
            return obj['specialist__last_name']
        return ""
