"""Archivo para Autorizaciones."""
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from api.models import Client, User
from api.serializers.authorization import ClientAuthorization, UserStatusSerializer
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status, permissions
from rest_framework.response import Response
from django.http import Http404
from api.serializers.actors import ClientSerializer


# Vista para Listar y Crear Clientes
class ClientListView(ListCreateAPIView):
    """Lista todos los clientes para listado de autorizacion."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = ClientAuthorization

    # Funcion personalizada para
    # devolver los clientes/usuarios para listado de autorizacion
    def list(self, request):
        """Lista de Clientes por autorizar."""
        # en dado caso que exista el parametro "main_specialist", se devuelve
        # el listado de especialistas asociados, caso contrario devuelve todos
        condition_status = ''
        condition_date = ''
        if "status" in request.query_params:
            status = request.query_params["status"]
            condition_status = " AND api_user.status = {}".format(status)
        if "from_date" in request.query_params and "until_date" in request.query_params:
            from_date = request.query_params["from_date"]
            until_date = request.query_params["until_date"]
            condition_date = " AND api_user.date_joined BETWEEN '{}' AND '{}'".format(from_date, until_date)
            
        condition = "{} {}".format(condition_status, condition_date)
        query_raw = """SELECT
                        seller.`code` AS code_seller,
                    IF (
                        api_client.type_client = 'b',
                        api_client.business_name,
                        CONCAT(
                            api_user.first_name,
                            ' ',
                            api_user.last_name
                        )
                    ) AS `name`,
                    IF (
                        api_client.type_client = 'b',
                        api_user.ruc,
                        api_user.document_number
                    ) AS document,
                    IF (
                        api_client.type_client = 'b',
                        'RUC',
                        api_user.document_type
                    ) AS document_type,
                     api_user.`status`,
                     api_user.id AS id,
                     date(api_user.date_joined) AS date_join
                    FROM
                        api_user
                    INNER JOIN api_role ON api_user.role_id = api_role.id
                    INNER JOIN api_client ON api_client.user_ptr_id = api_user.id
                    LEFT JOIN api_user AS seller ON api_client.seller_asigned_id = seller.id
                    WHERE
                        api_user.role_id = 2 {condition}
                    ORDER BY
                        api_user.`status` ASC,
                        api_user.updated_at DESC""".format(condition=condition)

        queryset = User.objects.raw(query_raw) # params={'condition': condition}
        serializer = ClientAuthorization(queryset, many=True)

        # pagination
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class ChangeStatusClientView(APIView):
    """Vista solo para que el admin pueda cambiar estatus a un cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAdminUser,)

    def get_object(self, pk):
        """Obtener objeto."""
        try:
            obj = Client.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except Client.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Actualizar Objeto."""
        data = request.data
        client = self.get_object(pk)
        serializer = UserStatusSerializer(client, data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
