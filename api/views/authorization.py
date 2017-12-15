from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from api.models import Client, User
from api.serializers.authorization import ClientAuthorization
from api.permissions import IsAdminOrOwner
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status, permissions
from rest_framework.response import Response

# Vista para Listar y Crear Clientes
class ClientListView(ListCreateAPIView):
    # Lista todos los clientes para listado de autorizacion
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = ClientAuthorization

    # Funcion personalizada para
    # devolver los clientes/usuarios para listado de autorizacion
    def list(self, request):
        # en dado caso que exista el parametro "main_specialist", se devuelve
        # el listado de especialistas asociados, caso contrario devuelve todos

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
                        'ruc',
                        api_user.document_type
                    ) AS document_type,
                     api_user.`status`,
                     api_user.id as pk,
                     1 as id,
                     date(api_user.date_joined) AS date_join
                    FROM
                        api_user
                    INNER JOIN api_role ON api_user.role_id = api_role.id
                    INNER JOIN api_client ON api_client.user_ptr_id = api_user.id
                    LEFT JOIN api_user AS seller ON api_client.seller_asigned_id = seller.id
                    WHERE
                        api_user.role_id = 2
                    ORDER BY
                        api_user.`status` ASC,
                        api_user.updated_at ASC"""

        queryset = User.objects.raw(query_raw)

        serializer = ClientAuthorization(queryset, many=True)

        # pagination
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
