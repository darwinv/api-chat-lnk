"""Vista de Estado de Cuenta."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from api.utils.validations import Operations
from api.serializers.notification import NotificationSerializer


class PendingNotificationView(APIView):
    """Vista de notificaciones pendientes, devuelve segun rol."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Funcion devolver data segun rol."""
        pk = Operations.get_id(self, request)
        import pdb; pdb.set_trace()
        serializer = NotificationSerializer(pk)
        return Response(serializer.data)
