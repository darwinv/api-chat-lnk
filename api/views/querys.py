from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from api.models import Query
# from api.serializers import ClientSerializer
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
import django_filters.rest_framework
# from api.serializers import UserSerializer, CategorySerializer, SpecialistSerializer
from api.serializers.query import QuerySerializer
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
# from rest_framework import generics
import pdb


class QueryListView(APIView):
    def get(self, request):
        querys = Query.objects.all()
        serializer = QuerySerializer(querys, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = QuerySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
