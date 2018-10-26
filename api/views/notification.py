"""Vista de Estado de Cuenta."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from api.utils.validations import Operations
from api.serializers.notification import NotificationClientSerializer
from api.serializers.notification import NotificationSpecialistSerializer
from api.utils.parameters import Params
from api.models import Client, Specialist


class PendingNotificationView(APIView):
    """Vista de notificaciones pendientes, devuelve segun rol."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Funcion devolver data segun rol."""
        user_id = Operations.get_id(self, request)
        if request.user.role_id == Params.ROLE_CLIENT:
            queryset = Client.objects.filter(pk=user_id)
            serializer = NotificationClientSerializer(queryset)
            return Response(serializer.data)
        elif request.user.role_id == Params.ROLE_SPECIALIST:
            queryset = Specialist.objects.filter(pk=user_id)
            serializer = NotificationSpecialistSerializer(queryset)
            return Response(serializer.data)
        return Response(serializer.data)
