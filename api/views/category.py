from rest_framework.views import APIView
from api.models import Category
from api.serializers.category import CategorySerializer
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
import django_filters.rest_framework
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
import pdb

class CategoryListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get(self, request):
        # Category.objects.all()
        # devuelve solo las especialidades con especialista principal
        specialities = Category.objects.filter(specialist__type_specialist='m')
        serializer = CategorySerializer(specialities, many=True)
        return Response(serializer.data)

class CategoryDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
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
