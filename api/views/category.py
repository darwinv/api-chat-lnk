from rest_framework.views import APIView
from api.models import Category
from api.serializers.category import CategorySerializer
from api.permissions import IsAdminUserOrReadOnly
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
import django_filters.rest_framework
from django.http import Http404
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.pagination import PageNumberPagination
import pdb

class CategoryListView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminUserOrReadOnly)
    def get(self, request):
        specialities = Category.objects.all()
        serializer = CategorySerializer(specialities, many=True)
        return Response(serializer.data)

class CategoryDetailView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminUserOrReadOnly)
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
# ------------ Fin de Categorias o Especialidades -----------------
