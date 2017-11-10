from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from api.models import Query, Specialist, Message
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, serializers
import django_filters.rest_framework
# from api.serializers import UserSerializer, CategorySerializer, SpecialistSerializer
from api.serializers.query import QuerySerializer, QueryListSerializer, MessageSerializer
from api.serializers.query import QueryDetailSerializer, QueryUpdateStatusSerializer
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from api.permissions import IsAdminOnList, IsAdminOrOwner, IsOwner
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasReadWriteScope, TokenHasScope
# import pdb


class QueryListView(ListCreateAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.AllowAny]
    queryset = Query.objects.all()
    serializer_class = QueryListSerializer

    def list(self, request):
        status = request.query_params.get('status', None)
        try:
            queryset = Query.objects.filter(client_id=request.query_params["client"])
            # si se envia la categoria se filtra por la misma, en caso contrario
            # devuelve todas
            if status is not None:
                if status == 'absolved':
                    queryset = Query.objects.filter(Q(status=6) | Q(status=7),
                                                client_id=request.query_params["client"])
                elif status == 'pending':
                    queryset = Query.objects.filter(status__lte=5,
                                                    client_id=request.query_params["client"])
                else:
                    raise serializers.ValidationError(detail="Invalid status")

            if 'category' in request.query_params:
                queryset = Query.objects.filter(client_id=request.query_params["client"],
                                                category_id=request.query_params["category"])
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

            serializer = QueryListSerializer(queryset, many=True)
            # pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            return Response(serializer.data)
        except Exception as e:
            string_error = u"Exception " + str(e)
            raise serializers.ValidationError(detail=string_error)

    def post(self, request):
        data = request.data
        # import pdb; pdb.set_trace()
        try:
            data["message"]["specialist"] = Specialist.objects.get(type_specialist="m",
                                                            category_id=data["category"])

            serializer = QuerySerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_201_CREATED)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            string_error = u"Exception: " + str(e) + " required"
            raise serializers.ValidationError(detail=string_error)


class QueryDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    def get_object(self, pk):
        try:
            return Query.objects.get(pk=pk)
        except Query.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        # si el argumento lastmsg existe, se debe volver,
        # el ultimo mensaje de consulta, por detalle
        # android especifico
        if 'last_msg' in request.query_params:
            # import pdb; pdb.set_trace()
            msg = Message.objects.filter(query_id=pk).last()
            serializer = MessageSerializer(msg)
        else:
            query = self.get_object(pk)
            serializer = QueryDetailSerializer(query)
        return Response(serializer.data)

    def put(self, request, pk):
        data = request.data
        query = self.get_object(pk)
        if 'status' in data or 'calification' in data:
            serializer = QueryUpdateStatusSerializer(query, data, partial=True)
        else:
            serializer = QuerySerializer(query, data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
