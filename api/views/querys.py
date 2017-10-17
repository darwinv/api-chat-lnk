from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from api.models import Query
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, serializers
import django_filters.rest_framework
# from api.serializers import UserSerializer, CategorySerializer, SpecialistSerializer
from api.serializers.querys import QuerySerializer
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
# from rest_framework import generics
import pdb


class QueryListView(ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Query.objects.all()
    serializer_class = QuerySerializer

    def list(self, request):
        # pdb.set_trace()
        try:
            queryset = Query.objects.filter(client_id=request.query_params["client"])
            # si se envia la categoria se filtra por la misma, en caso contrario
            # devuelve todas
            if 'category' in request.query_params:
                status = request.query_params.get('status', None)
                if status is not None:
                    if status == 'absolved':
                        queryset = Query.objects.filter(Q(status=6) | Q(status=7),
                                                    client_id=request.query_params["client"],
                                                    category_id=request.query_params["category"])
                    elif status == 'pending':
                        queryset = Query.objects.filter(status__lte=5,
                                                        client_id=request.query_params["client"],
                                                        category_id=request.query_params["category"])
                    else:
                        queryset = Query.objects.filter(client_id=request.query_params["client"],
                                                        category_id=request.query_params["category"])

            serializer = QuerySerializer(queryset, many=True)
            # pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            return Response(serializer.data)
        except Exception as e:
            string_error = u"The param(s) " + str(e) + " is mandatory"
            raise serializers.ValidationError(detail=string_error)

    # def get_queryset(self):
    #     """
    #     Optionally restricts the returned purchases to a given user,
    #     by filtering against a `username` query parameter in the URL.
    #     """
    #     queryset = Purchase.objects.all()
    #     username = self.request.query_params.get('username', None)
    #     if username is not None:
    #         queryset = queryset.filter(purchaser__username=username)
    #     return queryset
