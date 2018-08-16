"""Vista  de datos estaticos."""
from rest_framework.views import APIView
from api.models import Objection
from api.serializers.static_data import ObjectionsSerializer
from rest_framework.response import Response
# from rest_framework import status, permissions, viewsets
# import django_filters.rest_framework
# from django.http import Http404


class ObjectionsListView(APIView):
    """listado de objeciones."""

    def get(self, request):
        # Category.objects.all()
        objections = Objection.objects.all()
        serializer = ObjectionsSerializer(objections, many=True)
        return Response(serializer.data)
