from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

# Vista para Listar y Crear Clientes
class TestOAuth(APIView):
    """Lista todos los clientes para listado de autorizacion."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # Funcion personalizada para
    # devolver los clientes/usuarios para listado de autorizacion
    def get(self, request):
        return Response()
