"""Vistas de Consultas."""
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from api.models import Query, Specialist, Message, Category, Role
from django.db.models import OuterRef, Subquery, F
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, serializers
import django_filters.rest_framework
from rest_framework import filters
from api.serializers.query import QuerySerializer, QueryListClientSerializer, MessageSerializer
from api.serializers.query import QueryDetailSerializer, QueryUpdateStatusSerializer
from api.serializers.query import QueryDetailLastMsgSerializer, QueryChatClientSerializer
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from api.permissions import IsAdminOnList, IsAdminOrOwner, IsOwner, IsClient
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasReadWriteScope, TokenHasScope


class QueryListClientView(ListCreateAPIView):
    """Vista Consulta por parte del cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [IsClient]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Devolveremos las categorias para luego filtrar por usuario
    queryset = Category.objects.all()
    serializer_class = QueryListClientSerializer

    def list(self, request):
        """List."""
        user_id = request.user.id
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
    # def get_queryset(self):
    #     """Traer Listado de Especialidades con consultas pendientes."""
    #     user = self.request.user
    #     # import pdb; pdb.set_trace()
    #     if user.role == Role.objects.get(name='client'):
    #         # import pdb; pdb.set_trace()
    #         Category.objects.all()
    #         return Category.objects.all()
    #     else:
    #         pass
        # c.query.filter(client_id=user.id)
        # Query.objects.filter(client_id=user.id)
        # val = Category.objects.filter()



# listado de las consultas
    # def list(self, request):
            # import pdb; pdb.set_trace()
        # status = request.query_params.get('status', None)
        # try:
        #     queryset = Query.objects.filter(client_id=request.query_params["client"])
        #     # si se envia la categoria se filtra por la misma, en caso contrario
        #     # devuelve todas
        #     if status is not None:
        #         if status == 'absolved':
        #             queryset = Query.objects.filter(Q(status=6) | Q(status=7),
        #                                         client_id=request.query_params["client"])
        #         elif status == 'pending':
        #             queryset = Query.objects.filter(status__lte=5,
        #                                             client_id=request.query_params["client"])
        #         else:
        #             raise serializers.ValidationError(detail="Invalid status")
        #
        #     if 'category' in request.query_params:
        #         queryset = Query.objects.filter(client_id=request.query_params["client"],
        #                                         category_id=request.query_params["category"])
        #         if status is not None:
        #             if status == 'absolved':
        #                 queryset = Query.objects.filter(Q(status=6) | Q(status=7),
        #                                             client_id=request.query_params["client"],
        #                                             category_id=request.query_params["category"])
        #             elif status == 'pending':
        #                 queryset = Query.objects.filter(status__lte=5,
        #                                                 client_id=request.query_params["client"],
        #                                                 category_id=request.query_params["category"])
        #             else:
        #                 queryset = Query.objects.filter(client_id=request.query_params["client"],
        #                                                 category_id=request.query_params["category"])
        #     if 'order' in request.query_params:
        #         # se concatena el order en caso de enviarse
        #         if request.query_params["order"] == 'desc':
        #             queryset = queryset.order_by('-created_at')
        #
        #     serializer = QueryListSerializer(queryset, many=True)
        #     # pagination
        #     page = self.paginate_queryset(queryset)
        #     if page is not None:
        #         serializer = self.get_serializer(page, many=True)
        #         return self.get_paginated_response(serializer.data)
        #     return Response(serializer.data)
        # except Exception as e:
        #     string_error = u"Exception " + str(e)
        #     raise serializers.ValidationError(detail=string_error)

#   Crear Consulta
    def post(self, request):
        """Metodo para Crear consulta."""
        data = request.data
        # devolver especialista principal segun categoria
        # try:
        #     data["message"]["specialist"] = Specialist.objects.get(type_specialist="m",
        #                                                     category_id=data["category"])
        #
        serializer = QuerySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     string_error = u"Exception: " + str(e) + " required"
        #     raise serializers.ValidationError(detail=string_error)

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
    permission_classes = [IsClient]
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
        client = request.user.id

        queryset = Message.objects.values('id','nick', 'code', 'message', 'created_at', 'msg_type',
'viewed','query_id')\
                               .annotate(title=F('query__title',),status=F('query__status',),\
                               calification=F('query__calification',),\
                               category_id=F('query__category_id',))\
                               .filter(query__client_id=client, query__category_id=category)\
                               .order_by('-created_at')

        serializer = QueryChatClientSerializer(queryset, many=True)
        serializer = None

        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
