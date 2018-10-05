"""Vista de MAtch."""
from api.permissions import IsAdminOrClient
from rest_framework.generics import ListCreateAPIView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status, permissions
from api.utils.validations import Operations
from rest_framework.response import Response
from api.serializers.match import MatchSerializer


class MatchListClientView(ListCreateAPIView):
    """Vista Match cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrClient]

    def post(self, request):
        """Metodo para Solicitar Match."""
        # Devolvemos el id del usuario
        user_id = Operations.get_id(self, request)
        data = request.data
        data["client"] = user_id
        serializer = MatchSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
