"""Vistas de Consultas."""
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from api.models import Query, Message, Category
from api.permissions import IsAdminOrClient
from api.utils.validations import Operations
from api.serializers.query import QuerySerializer, QueryListClientSerializer, MessageSerializer
from api.serializers.query import QueryDetailSerializer, QueryUpdateStatusSerializer
from api.serializers.query import QueryDetailLastMsgSerializer, QueryChatClientSerializer
from django.db.models import OuterRef, Subquery, F
from django.http import Http404
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from api import pyrebase
from channels import Group
import json


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
        # tomamos del token el id de usuarios
        data["client"] = user_id
        serializer = QuerySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # pyrebase.chat_firebase_db(data, serializer.data["id"])
            # -- Aca una vez creada la data, cargar el mensaje directo a
            # -- la sala de chat en channels (usando Groups)
            # envio = dict(handle=serializer.data["code_client"], message=serializer.data['messages'][0]["message"])
            # Group('chat-'+str(label)).send({'text': json.dumps(envio)})
            return Response(serializer.data, status.HTTP_201_CREATED)
        # import pdb; pdb.set_trace()
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

# Detall de consulta
class QueryDetailView(APIView):
    # se debe definir todos los sets de permisos
    # ejemplo solo el principal puede derivar
    # solo el cliente puede preguntar, etc
    permission_classes = [permissions.AllowAny]
    def get_object(self, pk):
        try:
            return Query.objects.get(pk=pk)
        except Query.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        # si el argumento lastmsg existe, se debe volver,
        # el ultimo mensaje de consulta, por detalle
        # (android especifico)
        if 'last_msg' in request.query_params:
            # import pdb; pdb.set_trace()
            msg = Message.objects.filter(query_id=pk).last()
            serializer = MessageSerializer(msg)
        # se devuelve el ultimo query solicitado
        # (notificacion en android)
        elif 'query_last_msg' in request.query_params:
            query = self.get_object(pk)
            serializer = QueryDetailLastMsgSerializer(query)
        else:
            query = self.get_object(pk)
            serializer = QueryDetailSerializer(query)
        return Response(serializer.data)

    # actualizacion
    def put(self, request, pk):
        data = request.data
        query = self.get_object(pk)
        # si se envia status o calification se actualiza usando otro serializer
        if 'status' in data or 'calification' in data:
            serializer = QueryUpdateStatusSerializer(query, data, partial=True)
        else:
            # en caso contrario se envian mensjaes
            serializer = QuerySerializer(query, data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Devolver el detalle de una ultima consulta filtrada por categoria
# servicio pedido para android en notificaciones
class QueryLastView(APIView):

    permission_classes = [permissions.AllowAny]
    def get_object(self,category):
        try:
            # import pdb; pdb.set_trace()
            return Query.objects.filter(category_id=category).all().last()
        except Query.DoesNotExist:
            raise Http404

    def get(self, request, category):
        query = self.get_object(category)
        serializer = QueryDetailLastMsgSerializer(query)
        return Response(serializer.data)


# Para Crear y Listado de consultas
class QueryChatClientView(ListCreateAPIView):
    """Vista Consulta."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [IsAdminOrClient]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Devolveremos las categorias para luego filtrar por usuario
    # queryset = Category.objects.all()
    serializer_class = QueryChatClientSerializer


    def list(self, request):
        """
            Listado de queries y sus respectivos mensajes para un cliente
        """
        if not 'category' in request.query_params:
            raise Http404

        category = request.query_params['category']
        client = Operations.get_id(self, request)

        if not client:
            raise Http404

        queryset = Message.objects.values('id','nick', 'code', 'message', 'created_at', 'msg_type',
'viewed','query_id')\
                           .annotate(title=F('query__title',),status=F('query__status',),\
                           calification=F('query__calification',),\
                           category_id=F('query__category_id',))\
                           .filter(query__client_id=client, query__category_id=category)\
                           .order_by('-created_at')

        # Retorno 404 para ahorrar tiempo de ejecucion
        if not queryset:
            raise Http404


        serializer = QueryChatClientSerializer(queryset, many=True)

        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
