"""Vista de Estado de Cuenta."""
from rest_framework.views import APIView
from api.serializers.payment import PaymentSerializer
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
import django_filters.rest_framework
from api.utils.validations import Operations
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.http import Http404
from api.models import Specialist
from rest_framework.pagination import PageNumberPagination
from api.permissions import IsAdminOrSeller


# Vista para estado de cuenta de especialista
class SpecialistAccountView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Specialist.objects.get(pk=pk)
        except Specialist.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        specialist = self.get_object(pk)
        serializer = SpecialistAccountSerializer(specialist)
        return Response(serializer.data)
