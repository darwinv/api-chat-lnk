"""Vistas de Consultas."""
# paquetes de python
import json
import threading
import os
import boto3
import uuid
# paquetes de django
from django.db.models import OuterRef, Subquery, F, Count
from django.http import Http404, HttpResponse
# paquetes de terceros
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from channels import Group
# llamadas de nuestro propio proyecto
from api import pyrebase
from api.models import Query, Message, Category, Specialist, Client
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
from api.serializers.query import QueryResponseSerializer, ReQuerySerializer
from api.serializers.query import QueryQualifySerializer
from api.serializers.actors import SpecialistMessageListCustomSerializer
from api.serializers.actors import PendingQueriesSerializer
from botocore.exceptions import ClientError
from api.utils.tools import s3_upload_file, remove_file, resize_img
from api.utils.parameters import Params
import sys


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
        # import pdb; pdb.set_trace()
        serializer = QuerySerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            category = serializer.data["category"]
            lista = list(serializer.data['message'].values())
            # Se actualiza la base de datos de firebase para el mensaje
            if 'test' not in sys.argv:
                pyrebase.chat_firebase_db(serializer.data["message"],
                                          serializer.data["room"])
            # Se actualiza la base de datos de firebase listado
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

            data_queries = Query.objects.values('id', 'title', 'status', 'specialist')\
                                        .annotate(
                                            message=Subquery(
                                                mess.values('message')))\
                                        .annotate(
                                            date_at=Subquery(
                                                mess.values('created_at')))\
                                        .filter(client=user_id,
                                                specialist=serializer_tmp.data[0]['specialist'],
                                                status=1)\
                                        .annotate(count=Count('id'))\
                                        .order_by('-message__created_at')

            query_pending = PendingQueriesSerializer(data_queries, many=True)
            lista_d = {Params.PREFIX['query']+str(l['id']): l for l in query_pending.data}
            if 'test' not in sys.argv:
                pyrebase.createListMessageClients(serializer_tmp.data,
                                                  serializer.data["query_id"],
                                                  serializer.data["status"],
                                                  user_id,
                                                  serializer_tmp.data[0]['specialist'],
                                                  queries_list=lista_d
                                                  )

            # -- Aca una vez creada la data, cargar el mensaje directo a
            # -- la sala de chat en channels (usando Groups)
            sala = str(user_id) + '-' + str(serializer.data["category"])
            Group('chat-'+str(sala)).send({'text': json.dumps(lista)})
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            # print(serializer.errors)
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
            # Actualizamos el nodo de mensajes segun su sala
            if 'test' not in sys.argv:
                pyrebase.chat_firebase_db(serializer.data["message"],
                                          serializer.data["room"])
                # Actualizamos el listado de especialidades en Firebase
                pyrebase.categories_db(client_id,
                                       category_id, lista[-1]["timeMessage"])
            # sala es el cliente_id y su la categoria del especialista
            sala = str(query.client.id) + '-' + str(category_id)

            Group('chat-'+str(sala)).send({'text': json.dumps(lista)})
            for li in lista:
                if li['messageReference'] is not None and li['messageReference'] != 0:
                    ms_ref = li['messageReference']

            gp = GroupMessage.objects.get(message__id=ms_ref)
            msgs = gp.message_set.all()

            if 'test' not in sys.argv:
                pyrebase.update_status_group_messages(msgs, gp.status)
            msgs_query = query.message_set.all()
            requeries = query.available_requeries
            data_update = {
                "status": query.status,
                "availableRequeries": requeries
                }

            if 'test' not in sys.argv:
                pyrebase.update_status_querymessages(data_msgs=msgs_query,
                                                     data=data_update)
            # actualizo el querycurrent del listado de mensajes
            data = {'status': 3,
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
            sala = str(query.client.id) + '-' + str(category_id)

            Group('chat-'+str(sala)).send({'text': json.dumps(lista)})
            # actualizo el querycurrent del listado de mensajes
            for li in lista:
                if li['messageReference'] is not None and li['messageReference'] != 0:
                    ms_ref = li['messageReference']

            gp = GroupMessage.objects.get(message__id=ms_ref)
            msgs = gp.message_set.all()

            if 'test' not in sys.argv:
                pyrebase.update_status_group_messages(msgs, gp.status)
            msgs_query = query.message_set.all()
            requeries = lista[0]['query']['availableRequeries']

            data_update = {
                "status": query.status,
                "availableRequeries": requeries
                }
            if 'test' not in sys.argv:
                pyrebase.update_status_querymessages(data_msgs=msgs_query,
                                                     data=data_update)
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
        if not specialist:
            raise Http404

        queryset = Message.objects.values('id', 'code', 'message', 'created_at', 'msg_type', 'viewed',
                                          'query_id', 'query__client_id', 'message_reference', 'specialist_id', 'content_type', 'file_url')\
                          .annotate(title=F('query__title',), status=F('query__status',),
                                    qualification=F('query__qualification',),
                                    category_id=F('query__category_id',))\
                          .filter(query__client_id=client, query__specialist_id=specialist)\
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

        queryset = Message.objects.values('id', 'code', 'message', 'created_at', 'msg_type', 'viewed',
                                          'query_id', 'query__client_id', 'message_reference', 'specialist_id', 'content_type', 'file_url')\
                          .annotate(title=F('query__title',), status=F('query__status',),\
                                    qualification=F('query__qualification',),\
                           category_id=F('query__category_id',))\
                           .filter(query__client_id=client, query__category_id=category)\
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
        # import pdb; pdb.set_trace()
        # Cargamos el listado de archivos adjuntos
        msgs = request.data["message_id"].split(',')
        files = request.FILES.getlist('file')

        # Empezamos a subir cada archivo por hilo separado
        threads = []
        i = 0
        for file in files:
            print(msgs[i])
            t = threading.Thread(target=self.upload, args=(file, msgs[i]))
            threads.append(t)
            i = i + 1
        for x in threads:
            x.start()
        # # Wait for all of them to finish
        for x in threads:
            x.join()

        return HttpResponse(status=200)

    def upload(self, file, msg_id):
        """Funcion para subir archivos."""
        resp = True  # variable bandera
        name_file, extension = os.path.splitext(file.name)
        filename = str(uuid.uuid4())
        name = filename + extension
        # lo subimos a Amazon S3
        url = s3_upload_file(file, name)
        # generamos la miniatura
        thumb = resize_img(file, 256)
        if thumb:
            name_file_thumb, extension_thumb = os.path.splitext(thumb.name)
            url_thumb = s3_upload_file(thumb, filename + '-thumb' + extension_thumb)
            remove_file(thumb)
        else:
            url_thumb = ""

        # devolvemos el mensaje con su id correspondiente
        ms = Message.objects.get(pk=int(msg_id))
        ms.file_url = url
        ms.file_preview_url = url_thumb
        ms.save()
        s3 = boto3.client('s3')
        # Evaluamos si el archivo se subio a S3
        try:
            s3.head_object(Bucket='linkup-photos', Key=name)
        except ClientError as e:
            resp = int(e.response['Error']['Code']) != 404
        # Si no se ha subido se actualiza el estatus en firebase

        if resp is False:
            pyrebase.mark_failed_file(room=ms.room, message_id=ms.id)
        else:
            # Actualizamos el status en firebase
            data = {"uploaded": 2, "fileUrl": url, "filePreviewUrl": url_thumb}
            r = pyrebase.mark_uploaded_file(room=ms.room, message_id=ms.id,
                                            data=data)
            print(r)


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
                pyrebase.updateStatusQueryAccept(specialist,
                                                 query.client.id, pk)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class DeclineRequeryView(APIView):
    """Vista Declinar Reconsulta"""
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
            pyrebase.update_status_querymessages(msgs, {"status": 4})
            # import pdb; pdb.set_trace()
            for ms in msgs:
                GroupMessage.objects.filter(message__id=ms.id).update(status=2)
            # import pdb; pdb.set_trace()
            if 'test' not in sys.argv:
                pyrebase.update_status_group_messages(msgs, 2)
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
        serializer = QueryDeriveSerializer(query, data=data)
        if serializer.is_valid():
            serializer.save()
            if 'test' not in sys.argv:
                pyrebase.updateStatusQueryDerive(specialist,
                                                 data["specialist"], query)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class QueryDeclineView(APIView):
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
        serializer = QueryDeclineSerializer(query, data=request.data,
                                            context=context)

        if serializer.is_valid():
            serializer.save()
            if 'test' not in sys.argv:
                pyrebase.updateStatusQueryDerive(specialist,
                                                 main_specialist.id, query)
            return Response(serializer.data, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


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
            msgs = query.message_set.all()
            if 'test' not in sys.argv:
                pyrebase.update_status_querymessages(msgs, serializer.data)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ReadPendingAnswerView(APIView):
    """Vista de lectura de respuestas no vistos del cliente."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def post(self, request):
        """Enviar data."""
        data = request.data
        client_id = Operations.get_id(self, request)
        mesgs_res = Message.objects.filter(
            viewed=0, msg_type='a', query__client=client_id,
            query__category=data["category"])
        if 'test' not in sys.argv:
            pyrebase.set_message_viewed(mesgs_res)
        r = mesgs_res.update(viewed=1)
        if 'test' not in sys.argv:
            pyrebase.categories_db(client_id, data["category"])
        return Response({'resp': r}, status.HTTP_200_OK)
