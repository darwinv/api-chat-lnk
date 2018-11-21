"""Vistas de Consultas."""
# paquetes de python
import json
import threading
import os
import sys
import boto3
# paquetes de django
from django.db.models import OuterRef, Subquery, F, Count
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from rest_framework import serializers
# paquetes de terceros
from api.models import Declinator
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from channels import Group
# llamadas de nuestro propio proyecto
from api import pyrebase
from api.models import Query, Message, Category, Specialist, Client, User
from api.models import GroupMessage, SpecialistMessageList_sp
from api.permissions import IsAdminOrClient, IsAdminOrSpecialist, IsSpecialist
from api.permissions import IsAdminReadOrSpecialistOwner, IsClient
from api.permissions import IsClientOrSpecialistAndOwner
from api.utils.validations import Operations
from api.serializers.query import QuerySerializer, QueryListClientSerializer
from api.serializers.query import QueryMessageSerializer
from api.serializers.query import QueryDeriveSerializer, QueryAcceptSerializer
from api.serializers.query import QueryDetailLastMsgSerializer
from api.serializers.query import ChatMessageSerializer, QueryDeclineSerializer
from api.serializers.query import QueryListDeclineSerializer
from api.serializers.query import QueryResponseSerializer, ReQuerySerializer
from api.serializers.query import QueryQualifySerializer, DeclineReprSerializer
from api.serializers.actors import SpecialistMessageListCustomSerializer
from api.serializers.actors import PendingQueriesSerializer
from api.serializers.notification import NotificationSpecialistSerializer
from api.serializers.notification import NotificationClientSerializer
from botocore.exceptions import ClientError
from api.utils.tools import s3_upload_file, remove_file, resize_img, get_body
from api.utils.parameters import Params
from api.utils.querysets import get_queries_pending_to_solve
from fcm.fcm import Notification
from api.logger import manager
logger = manager.setup_log(__name__)


class QueryListClientView(ListCreateAPIView):
    """Vista Consulta por parte del cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrClient]
    # Devolveremos las categorias para luego filtrar por usuario
    queryset = Category.objects.all()
    serializer_class = QueryListClientSerializer

    def list(self, request):
        """List."""
        user_id = Operations.get_id(self, request)

        if not user_id:
            raise Http404

        # Se hace un subquery para traer los ultimos msjs.
        q_query = Query.objects.values('message__created_at')\
                               .filter(client_id=user_id, message__msg_type='q')\
                               .order_by('-message__created_at')

        # Se realiza la consulta tomando como subconsulta la consulta anterior
        queryset = Category.objects.annotate(fecha=Subquery(q_query.values('message__created_at')
                                                                   .filter(category_id=OuterRef('pk'))[:1]))\
                                   .order_by(F('fecha').desc())

        serializer = QueryListClientSerializer(queryset, context={'user': request.user}, many=True)

        return Response(serializer.data)


#   Crear Consulta
    def post(self, request):
        """Metodo para Crear consulta."""
        # Devolvemos el id del usuario
        user_id = Operations.get_id(self, request)
        # label = 1
        if not user_id:
            raise Http404
        data = request.data
        # tomamos del token el id de usuario (cliente en este caso)
        data["client"] = user_id
        serializer = QuerySerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            category = serializer.data["category"]
            lista = list(serializer.data['message'].values())
            # Se actualiza la base de datos de firebase para el mensaje
            if 'test' not in sys.argv:
                pyrebase.node_query(serializer.data["obj_query"],
                                    serializer.data["query_id"],
                                    serializer.data["room"])

                pyrebase.chat_firebase_db(serializer.data["message"],
                                          serializer.data["room"])
            #  Se actualiza la base de datos de firebase listado
            # de sus especialidades
            if 'test' not in sys.argv:
                pyrebase.categories_db(user_id, category,
                                       lista[-1]["timeMessage"])

            data_set = SpecialistMessageList_sp.search(2, user_id, category,
                                                       0, "")

            serializer_tmp = SpecialistMessageListCustomSerializer(data_set,
                                                                   many=True)

            # Se devuelve las ultimas consultas pendientes por responder
            # por cliente
            # Primer una subconsulta para buscar el ultimo registro de mensaje
            mess = Message.objects.filter(query=OuterRef("pk"))\
                                  .order_by('-created_at')[:1]
            # Luego se busca el titulo y su id de la consulta
            specialist_id = serializer_tmp.data[0]['specialist']

            data_queries = Query.objects.values('id', 'title', 'status', 'specialist')\
                                        .annotate(
                                            message=Subquery(
                                                mess.values('message')))\
                                        .annotate(
                                            date_at=Subquery(
                                                mess.values('created_at')))\
                                        .filter(client=user_id,
                                                specialist=specialist_id,
                                                status=1)\
                                        .annotate(count=Count('id'))\
                                        .order_by('-message__created_at')
            query_pending = PendingQueriesSerializer(data_queries, many=True)
            lista_d = {Params.PREFIX['query']+str(l['id']): l for l in query_pending.data}

            # determino el total de consultas pendientes (status 1 o 2)
            # y matchs por responder o pagar
            qset_spec = Specialist.objects.filter(pk=specialist_id)
            dict_pending = NotificationSpecialistSerializer(qset_spec).data
            badge_count = dict_pending["queries_pending"] + dict_pending["match_pending"]

            if 'test' not in sys.argv:
                # crea data de notificacion push
                body = get_body(lista[-1]["fileType"], lista[-1]["message"])
                data_notif_push = {
                    "title": serializer_tmp.data[0]['displayName'],
                    "body": body,
                    "sub_text": "",
                    "ticker": serializer.data["obj_query"]["title"],
                    "badge": badge_count,
                    "icon": serializer_tmp.data[0]['photo'],
                    "client_id": user_id,
                    "category_id": category,
                    "type": Params.TYPE_NOTIF["query_new"],
                    "queries_pending": dict_pending["queries_pending"],
                    "match_pending": dict_pending["match_pending"],
                    "query_id": serializer.data["query_id"]
                }


                # crea nodo de listado de mensajes
                pyrebase.createListMessageClients(serializer_tmp.data,
                                                  serializer.data["query_id"],
                                                  serializer.data["status"],
                                                  user_id,
                                                  specialist_id,
                                                  queries_list=lista_d)
                # envio de notificacion push
                Notification.fcm_send_data(user_id=specialist_id,
                                           data=data_notif_push)

            # -- Aca una vez creada la data, cargar el mensaje directo a
            # -- la sala de chat en channels (usando Groups)
            room_channel = str(user_id) + '-' + str(serializer.data["category"])

            # Se envian el query y sus mensajes por channels
            Group('chat-'+str(room_channel)).send({'text': json.dumps({
                        "eventType": 1,
                        "query": serializer.data["obj_query"]["title"],
                        "status": serializer.data["obj_query"]["status"],
                        "specialist": specialist_id,
                        "messages": lista
                    })})
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class QueryDetailSpecialistView(APIView):
    """Vista para que el especialista responda la consulta."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated,
                          IsAdminReadOrSpecialistOwner]

    def get_object(self, pk):
        """Obtener objeto."""
        try:
            obj = Query.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj.specialist)
            return obj
        except Query.DoesNotExist:
            raise Http404

    # Actualizar Consulta
    def put(self, request, pk):
        """Actualiza la consulta."""
        query = self.get_object(pk)
        user_id = Operations.get_id(self, request)
        # label = 1
        if not user_id:
            raise Http404
        data = request.data
        # tomamos del token el id de usuario (especialista en este caso)
        spec = Specialist.objects.get(pk=user_id)
        # No utilizamos partial=True, ya que solo actualizamos mensaje
        serializer = QueryResponseSerializer(query, data,
                                             context={'specialist': spec})
        if serializer.is_valid():
            serializer.save()
            lista = list(serializer.data['message'].values())
            client_id = serializer.data["client_id"]
            category_id = serializer.data["category"]
            cat = Category.objects.get(pk=category_id)

            if 'test' not in sys.argv:
                # Actualizamos el nodo de mensajes segun su sala
                pyrebase.chat_firebase_db(serializer.data["message"],
                                          serializer.data["room"])
                # Actualizamos el listado de especialidades en Firebase
                pyrebase.categories_db(client_id,
                                       category_id, lista[-1]["timeMessage"])

            # sala es el cliente_id y su la categoria del especialista
            room_channel = str(query.client.id) + '-' + str(category_id)


            # Se envian el query y sus mensajes por channels
            Group('chat-'+str(room_channel)).send({'text': json.dumps({
                        "eventType": 1,
                        "query": serializer.data["obj_query"]["title"],
                        "status": serializer.data["obj_query"]["status"],
                        "specialist": user_id,
                        "messages": lista
                    })})

            for row in lista:
                if row['messageReference'] is not None and row['messageReference'] != 0:
                    ms_ref = row['messageReference']

            group = GroupMessage.objects.get(message__id=ms_ref)
            msgs = group.message_set.all()

            # determino el total de consultas pendientes (status 3 o 5)
            # y matchs por pagar (status 4)
            qset_client = Client.objects.filter(pk=client_id)
            dict_pending = NotificationClientSerializer(qset_client).data
            badge_count = dict_pending["queries_pending"] + dict_pending["match_pending"]

            if 'test' not in sys.argv:
                pyrebase.update_status_group_messages(msgs, group.status)

                body = get_body(lista[-1]["fileType"], lista[-1]["message"])
                data_fcm = {
                    "title": ugettext(cat.name),
                    "body": body,
                    "sub_text": ugettext(cat.name),
                    "ticker": query.title,
                    "icon": cat.image,
                    "badge": badge_count,
                    "client_id":  query.client.id,
                    "type": Params.TYPE_NOTIF["query_answer"],
                    "category_id": category_id,
                    "queries_pending": dict_pending["queries_pending"],
                    "match_pending": dict_pending["match_pending"],
                    "query_id": query.id
                }
                Notification.fcm_send_data(user_id=client_id, data=data_fcm)

            requeries = query.available_requeries
            data_update = {
                "status": query.status,
                "availableRequeries": requeries
            }

            if 'test' not in sys.argv:
                pyrebase.update_status_query(query_id=query.id,
                                             data=data_update,
                                             room=serializer.data["room"])

            # actualizo el querycurrent del listado de mensajes
            data = {'status': query.status,
                    'date': lista[-1]["timeMessage"],
                    'message': lista[-1]["message"]}

            if 'test' not in sys.argv:
                pyrebase.update_status_query_current_list(user_id,
                                                          client_id, data)

            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class QueryDetailClientView(APIView):
    """Vista para reconsultar."""  # por ahora
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated,
                          IsClientOrSpecialistAndOwner]

    def get_object(self, pk):
        """Obtener objeto."""
        try:
            obj = Query.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj.client.id)
            return obj
        except Query.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Actualizar consulta."""
        query = self.get_object(pk)
        user_id = Operations.get_id(self, request)
        if not user_id:
            raise Http404
        data = request.data

        # No utilizamos partial=True, ya que solo actualizamos mensaje
        serializer = ReQuerySerializer(query, data)
        if serializer.is_valid():
            serializer.save()
            lista = list(serializer.data['message'].values())
            client_id = serializer.data["client_id"]
            category_id = serializer.data["category"]
            specialist_id = serializer.data["specialist_id"]
            # Actualizamos el nodo de mensajes segun su sala
            if 'test' not in sys.argv:
                pyrebase.chat_firebase_db(serializer.data["message"],
                                          serializer.data["room"])

            # Actualizamos el listado de especialidades en Firebase
            if 'test' not in sys.argv:
                pyrebase.categories_db(user_id, category_id,
                                       lista[-1]["timeMessage"])
            # sala es el cliente_id y su la categoria del especialista
            room_channel = str(query.client.id) + '-' + str(category_id)

            # Se envian el query y sus mensajes por channels
            Group('chat-'+str(room_channel)).send({'text': json.dumps({
                        "eventType": 1,
                        "query": serializer.data["obj_query"]["title"],
                        "status": serializer.data["obj_query"]["status"],
                        "specialist": serializer.data["specialist_id"],
                        "messages": lista
                    })})

            # actualizo el querycurrent del listado de mensajes
            for li in lista:
                if li['messageReference'] is not None and li['messageReference'] != 0:
                    ms_ref = li['messageReference']

            gp = GroupMessage.objects.get(message__id=ms_ref)
            msgs = gp.message_set.all()
            qset_spec = Specialist.objects.filter(pk=specialist_id)
            dict_pending = NotificationSpecialistSerializer(qset_spec).data
            badge_count = dict_pending["queries_pending"] + dict_pending["match_pending"]

            if 'test' not in sys.argv:
                us = User.objects.get(pk=user_id)
                if us.nick == '':
                    displayname = us.first_name + ' ' + us.last_name
                else:
                    displayname = us.nick

                # crea data de notificacion push
                body = get_body(lista[-1]["fileType"], lista[-1]["message"])
                data_notif_push = {
                    "title": displayname,
                    "body": body,
                    "sub_text": "",
                    "ticker": serializer.data["obj_query"]["title"],
                    "badge": badge_count,
                    "icon": us.photo,
                    "client_id": user_id,
                    "type": Params.TYPE_NOTIF["query_requery"],
                    "category_id": category_id,
                    "queries_pending": dict_pending["queries_pending"],
                    "match_pending": dict_pending["match_pending"],
                    "query_id": serializer.data["query_id"]
                }
                pyrebase.update_status_group_messages(msgs, gp.status)
                # envio de notificacion push
                Notification.fcm_send_data(user_id=specialist_id,
                                           data=data_notif_push)
            requeries = serializer.data['obj_query']['availableRequeries']

            data_update = {
                "status": query.status,
                "availableRequeries": requeries
                }
            if 'test' not in sys.argv:
                pyrebase.update_status_query(query.id, data_update,
                                             serializer.data["room"])
            data = {'status': 2,
                    'date': lista[-1]["timeMessage"],
                    'message': lista[-1]["message"]
                    }
            if 'test' not in sys.argv:
                pyrebase.update_status_query_current_list(specialist_id,
                                                          client_id,
                                                          data)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


# Devolver el detalle de una ultima consulta filtrada por categoria
# servicio pedido para android en notificaciones
class QueryLastView(APIView):

    permission_classes = [permissions.AllowAny]

    def get_object(self, category):
        try:
            # import pdb; pdb.set_trace()
            return Query.objects.filter(category_id=category).all().last()
        except Query.DoesNotExist:
            raise Http404

    def get(self, request, category):
        query = self.get_object(category)
        serializer = QueryDetailLastMsgSerializer(query)
        return Response(serializer.data)


class QueryChatSpecialistView(ListAPIView):
    """Vista de consultas en el chat por parte del especialista."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSpecialist)
    serializer_class = ChatMessageSerializer

    def get_object(self, pk):
        """Obtener cliente."""
        try:
            return Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """Listado de queries y sus respectivos mensajes para un cliente."""
        client = self.get_object(pk)
        specialist = Operations.get_id(self, request)
        
        specialist = Specialist.objects.get(pk=specialist)

        queryset = Message.objects.values('id', 'code', 'message', 'created_at', 
            'msg_type', 'viewed', 'query_id', 'query__client_id', 'message_reference', 
            'specialist_id', 'content_type', 'file_url', 'file_preview_url', 'query__specialist_id')\
                          .annotate(title=F('query__title',), status=F('query__status',),
                                    qualification=F('query__qualification',),
                                    category_id=F('query__category_id',),\
                                    group_status=F('group__status',))\
                          .filter(query__client_id=client, 
                            query__category_id=specialist.category)\
                          .order_by('-created_at')

        serializer = ChatMessageSerializer(queryset, many=True)
        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class QueryChatClientView(ListCreateAPIView):
    """Vista Consultas en el chat por parte del Cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrClient)
    serializer_class = ChatMessageSerializer

    def get_object(self, pk):
        """Obtener cliente."""
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """Listado de queries y sus respectivos mensajes para un especialista."""
        category = self.get_object(pk)
        client = Operations.get_id(self, request)

        if not client:
            raise Http404

        queryset = Message.objects.values('id', 'code', 'message', 'created_at', 
            'msg_type', 'viewed', 'query_id', 'query__client_id', 'message_reference', 
            'specialist_id', 'content_type', 'file_url', 'file_preview_url', 'query__specialist_id',
            'uploaded')\
                          .annotate(title=F('query__title',), status=F('query__status',),
                                    qualification=F('query__qualification',),
                                    category_id=F('query__category_id',),\
                                    group_status=F('group__status',))\
                          .filter(query__client_id=client,
                            query__category_id=category)\
                          .order_by('-created_at')

        serializer = ChatMessageSerializer(queryset, many=True)

        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class QueryUploadFilesView(APIView):
    """Subida de archivos para la consultas."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated,
                          IsClientOrSpecialistAndOwner]
    parser_classes = (JSONParser, MultiPartParser)

    def get_object(self, request, pk):
        """Devuelvo la consulta."""
        try:
            obj = Query.objects.get(pk=pk)
            if request.user.role_id == 2:
                owner = obj.client_id
            elif request.user.role_id == 3:
                owner = obj.specialist_id
            self.check_object_permissions(self.request, owner)
            return obj
        except Query.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Actualiza la consulta, subiendo archivos."""
        self.get_object(request, pk)
        files = request.FILES.getlist('file')
        if files:
            arch = files
        else:
            data = request.data.dict()
            arch = list(data.values())

        # Empezamos a subir cada archivo por hilo separado
        threads = []
        i = 0
        for file in arch:
            t = threading.Thread(target=self.upload, args=(file,))
            threads.append(t)
            i = i + 1

        for x in threads:
            x.start()

        # Wait for all of them to finish
        for x in threads:
            x.join()

        return HttpResponse(status=200)

    def upload(self, file):
        """Funcion para subir archivos."""

        ms = None  # Objeto mensajes
        resp = True  # variable bandera
        name_file, extension = os.path.splitext(file.name)
        msg_id = name_file.split("-")[-1]  # obtenemos el ultimo por (-)
        
        try:
            ms = Message.objects.get(pk=int(msg_id))

            # lo subimos a Amazon S3
            url = s3_upload_file(file, file.name)
            # generamos la miniatura
            thumb = resize_img(file, 256)
            if thumb:
                name_file_thumb, extension_thumb = os.path.splitext(thumb.name)
                url_thumb = s3_upload_file(thumb, name_file + '-thumb' + extension_thumb)
                remove_file(thumb)
            else:
                url_thumb = ""

            # Actualizamos el modelo mensaje
            ms.file_url = url
            ms.file_preview_url = url_thumb

            s3 = boto3.client('s3')
            # Evaluamos si el archivo se subio a S3
            try:
                s3.head_object(Bucket='linkup-photos', Key=file.name)
            except ClientError as e:
                resp = int(e.response['Error']['Code']) != 404

        except Exception as e:
            logger.error("subir archivo, error general, m_ID: {} - ERROR: {} ".format(msg_id, e))
            resp = False


        if resp is False:
            if 'test' not in sys.argv:
                ms_status = 5
                if ms:
                    pyrebase.mark_failed_file(room=ms.room, message_id=ms.id)
                    logger.error("file dont put, room:{} -m:{} ".format(ms.room, ms.id))
                    print("con objeto error")
                    ms.uploaded = 5
                    ms.save()
                else:
                    logger.error("file dont put, message_ID:{} ".format(msg_id))
                    print("sin objeto error")
        else:
            if 'test' not in sys.argv:
                # Actualizamos el status en firebase
                ms_status = 2
                data = {"uploaded": ms_status, "fileUrl": url, "filePreviewUrl": url_thumb}
                r = pyrebase.mark_uploaded_file(room=ms.room, message_id=ms.id,
                                                data=data)
                print(r)
                ms.uploaded = ms_status
                ms.save()

        if 'test' not in sys.argv:
            if ms:
                query = ms.query
                room_channel = str(query.client.id) + '-' + str(query.category.id)
                Group('chat-'+str(room_channel)).send({'text': json.dumps({
                        "eventType": 3,
                        "message": ms.id,
                        "filePreviewUrl": url_thumb,
                        "fileUrl": url,
                        "uploaded": ms_status
                    })})


class QueryMessageView(APIView):
    """Vista Consultas en el chat por parte del Cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSpecialist)

    def get(self, request, pk):
        """Listado de queries y sus respectivos mensajes para un especialista."""
        try:
            message = Query.objects.values('id', 'title', 'client__last_name',\
            'client__first_name', 'client__nick', 'client__photo')\
            .get(pk=pk)
        except Query.DoesNotExist:
            raise Http404

        serializer = QueryMessageSerializer(message, partial=True)
        return Response(serializer.data)


class QueryAcceptView(APIView):
    """Vista Aceptar Query"""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsSpecialist)

    def put(self, request, pk):
        """Listado de queries y sus respectivos mensajes para un especialista."""
        specialist = Operations.get_id(self, request)
        try:
            query = Query.objects.get(pk=pk, status=1, specialist=specialist)
        except Query.DoesNotExist:
            raise Http404

        data = {}
        data["status"] = 2
        serializer = QueryAcceptSerializer(query, data=data)
        if serializer.is_valid():
            serializer.save()
            if 'test' not in sys.argv:
                room = query.message_set.last().room
                pyrebase.updateStatusQueryAccept(specialist,
                                                 query.client.id, pk,
                                                 room)

                room_channel = str(query.client.id) + '-' + str(query.category.id)
                Group('chat-'+str(room_channel)).send({'text': json.dumps({
                        "eventType": 2,
                        "query": pk,
                        "data": {"status": data["status"]}
                    })})

            # Traemos todas las consultas pendientes por tomar accion por asignadas
            # a este especialista
            # msgs_pendings = Query.objects.filter(status=1, specialist=specialist)

            return Response({}, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class DeclineRequeryView(APIView):
    """Vista Declinar Reconsulta."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def post(self, request):
        """Actualizar mensajes de categoria."""
        user_id = Operations.get_id(self, request)
        category = request.data["category_id"]
        queries = Query.objects.filter(category=category, client=user_id,
                                       status=3)
        for query in queries:
            msgs = query.message_set.all()
            # import pdb; pdb.set_trace()
            if 'test' not in sys.argv:
                pyrebase.update_status_query(query.id, {"status": 4},
                                             msgs.last().room)
            # import pdb; pdb.set_trace()
            for ms in msgs:
                GroupMessage.objects.filter(message__id=ms.id).update(status=2)
            # import pdb; pdb.set_trace()
            if 'test' not in sys.argv:
                pyrebase.update_status_group_messages(msgs, 2)

                room_channel = str(query.client.id) + '-' + str(query.category.id)
                Group('chat-'+str(room_channel)).send({'text': json.dumps({
                        "eventType": 2,
                        "query": query.id,
                        "data": {"status": 4}
                    })})

        success = queries.update(status=4)
        if success:
            return Response({}, status.HTTP_200_OK)
        return Response({}, status.HTTP_400_BAD_REQUEST)


class QueryDeriveView(APIView):
    """Vista Derivar Query"""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsSpecialist)

    def put(self, request, pk):

        """Listado de queries y sus respectivos mensajes para un especialista."""
        specialist = Operations.get_id(self, request)
        try:
            query = Query.objects.get(pk=pk, status__lt=3,
                                      specialist=specialist)
        except Query.DoesNotExist:
            raise Http404

        data = {}
        data["status"] = 1
        data["specialist"] = request.data["specialist"]
        specialist_asoc_id = data["specialist"]
        serializer = QueryDeriveSerializer(query, data=data)
        if serializer.is_valid():
            serializer.save()
            qset_spec = Specialist.objects.filter(pk=specialist_asoc_id)
            dict_pending = NotificationSpecialistSerializer(qset_spec).data
            badge_count = dict_pending["queries_pending"] + dict_pending["match_pending"]
            if 'test' not in sys.argv:
                lista = list(serializer.data['message'].values())
                body = get_body(lista[-1]["fileType"], lista[-1]["message"])
                data_notif_push = {
                    "title": serializer.data['displayName'],
                    "body": body,
                    "sub_text": "",
                    "ticker": serializer.data["obj_query"]["title"],
                    "badge": badge_count,
                    "icon": serializer.data['photo'],
                    "client_id": serializer.data['client'],
                    "type": Params.TYPE_NOTIF["query_derived"],
                    "category_id": serializer.data['category'],
                    "queries_pending": dict_pending["queries_pending"],
                    "match_pending": dict_pending["match_pending"],
                    "query_id": serializer.data["query_id"]
                }
                # envio de notificacion push
                Notification.fcm_send_data(user_id=specialist_asoc_id,
                                           data=data_notif_push)

                pyrebase.updateStatusQueryDerive(specialist,
                                                 data["specialist"], query)

                room_channel = str(query.client.id) + '-' + str(query.category.id)
                Group('chat-'+str(room_channel)).send({'text': json.dumps({
                        "eventType": 2,
                        "query": pk,
                        "data": {"specialist": data["specialist"]}
                    })})

            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class QueryDeclineView(ListAPIView):
    """Vista Derivar Query"""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsSpecialist)

    def put(self, request, pk):

        """Listado de queries y sus respectivos mensajes para un especialista."""
        specialist = Operations.get_id(self, request)

        try:
            # Queris status menor a 3
            query = Query.objects.get(pk=pk, status__lt=3,
                                      specialist=specialist)
        except Query.DoesNotExist:
            raise Http404

        try:
            main_specialist = Specialist.objects.get(category=query.category,
                                                     type_specialist='m')
        except Specialist.DoesNotExist:
            raise Http404
        context = {}
        context["status"] = 1
        context["specialist"] = main_specialist
        context["specialist_declined"] = specialist
        main_specialist_id = main_specialist.id
        serializer = QueryDeclineSerializer(query, data=request.data,
                                            context=context)

        if serializer.is_valid():
            serializer.save()
            qset_spec = Specialist.objects.filter(pk=main_specialist_id)
            dict_pending = NotificationSpecialistSerializer(qset_spec).data
            badge_count = dict_pending["queries_pending"] + dict_pending["match_pending"]
            ser = DeclineReprSerializer(query)
            if 'test' not in sys.argv:
                data_notif_push = {
                    "title": ser.data['displayName'],
                    "body": ser.data["motive"],
                    "sub_text": "",
                    "ticker": ser.data["motive"],
                    "badge": badge_count,
                    "icon": ser.data['photo'],
                    "type": Params.TYPE_NOTIF["query_declined"],
                    "client_id": ser.data['client'],
                    "category_id": ser.data["category"],
                    "queries_pending": dict_pending["queries_pending"],
                    "match_pending": dict_pending["match_pending"],
                    "query_id": ser.data["query_id"]
                }
                pyrebase.updateStatusQueryDerive(specialist,
                                                 main_specialist_id, query)
                # envio de notificacion push
                Notification.fcm_send_data(user_id=main_specialist_id,
                                           data=data_notif_push)

                room_channel = str(query.client.id) + '-' + str(query.category.id)
                Group('chat-'+str(room_channel)).send({'text': json.dumps({
                        "eventType": 2,
                        "query": pk,
                        "data": {"specialist": main_specialist_id}
                    })})

            return Response(ser.data, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        """Obtener la lista con todos los planes del cliente."""
        declinators = Declinator.objects.filter(
            query=pk).values('message', 'specialist__first_name',
                             'specialist__last_name')

        serializer = QueryListDeclineSerializer(declinators, many=True)

        return Response(serializer.data)


class SetQualificationView(APIView):
    """Vista colocar calificacion ."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def get_object(self, pk):
        """Obtener objeto."""
        try:
            obj = Query.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj.client.id)
            return obj
        except Query.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Actualizar consulta."""
        query = self.get_object(pk)
        data = request.data
        serializer = QueryQualifySerializer(query, data=data)
        if serializer.is_valid():
            serializer.save()
            if 'test' not in sys.argv:
                room = query.message_set.last().room
                pyrebase.update_status_query(query.id, serializer.data, room)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ReadPendingAnswerView(APIView):
    """Vista de lectura de respuestas no vistos del cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsClient]
    required = _("required")

    def get_category(self, categ):
        """Obtener objeto."""
        try:
            obj = Category.objects.get(pk=categ)
            return obj
        except Category.DoesNotExist:
            raise serializers.ValidationError({"category": [str(categ)+' no existe']})

    def post(self, request):
        """Enviar data."""
        data = request.data
        client_id = Operations.get_id(self, request)

        if "category" in data:
            category = int(data["category"])
        else:
            raise serializers.ValidationError({'category': [self.required]})

        # Traer los mensajes que no han sido leidos y son respuestass del especialista
        mesgs_res = Message.objects.filter(
            viewed=False, msg_type='a', query__client=client_id,
            query__category=category)
        if mesgs_res:
            mesgs_res.update(viewed=1)

            # if 'test' not in sys.argv: #NO ACTUALIZAMOS CHAT
            #     pyrebase.set_message_viewed(mesgs_res)
            if 'test' not in sys.argv:
                pyrebase.categories_db(client_id, category)

        return Response({}, status.HTTP_200_OK)
