"""Vista de MAtch."""
import os
import boto3
from django.http import Http404, HttpResponse
from botocore.exceptions import ClientError
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from django.utils.translation import ugettext_lazy as _
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status, permissions
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from api.utils.validations import Operations
from api.serializers.match import MatchSerializer, MatchListClientSerializer
from api.serializers.match import MatchListSpecialistSerializer
from api.serializers.match import MatchListSerializer
from api.permissions import IsAdminOrClient, IsOwnerAndClient
from api.permissions import IsAdminOrSpecialist, IsAdmin
from api.models import Match, MatchFile
from api.utils.tools import s3_upload_file, remove_file, resize_img
from api.logger import manager
logger = manager.setup_log(__name__)


class MatchListClientView(ListCreateAPIView):
    """Vista Match cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrClient]

    def list(self, request):
        """Listado de Matchs."""
        user_id = Operations.get_id(self, request)
        queryset = Match.objects.filter(client_id=user_id)
        serializer = MatchListClientSerializer(queryset, many=True)
        return Response(serializer.data)

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

class MatchBackendListView(ListCreateAPIView):
    """Vista Match cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def list(self, request):
        """Listado de Matchs."""
        queryset = Match.objects.all()

        if 'status' in request.query_params:
            status = request.query_params["status"]
            queryset = queryset.filter(status=status)
        
        if 'payment_option_specialist' in request.query_params:
            payment_option_specialist = request.query_params["payment_option_specialist"]
            queryset = queryset.filter(payment_option_specialist=payment_option_specialist)

        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MatchListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MatchListSerializer(page, many=True)
        return Response(serializer.data)

class MatchListSpecialistView(ListCreateAPIView):
    """Vista Match cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSpecialist]

    def list(self, request):
        """Listado de Matchs."""
        user_id = Operations.get_id(self, request)
        queryset = Match.objects.filter(specialist=user_id)
        serializer = MatchListSpecialistSerializer(queryset, many=True)
        return Response(serializer.data)



class MatchUploadFilesView(APIView):
    """Subida de archivos para la consultas."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsOwnerAndClient]
    parser_classes = (JSONParser, MultiPartParser)

    def get_object(self, request, pk):
        """Devuelvo la consulta."""
        try:
            obj = Match.objects.get(pk=pk)
            owner = obj.client_id
            self.check_object_permissions(self.request, owner)
            return obj
        except Match.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Actualiza el match, subiendo archivos."""
        self.get_object(request, pk)
        files = request.FILES.getlist('file')
        errors_list = []
        if files:
            arch = files
        else:
            data = request.data.dict()
            arch = list(data.values())

        for file in arch:
            resp = self.upload(file=file)
            if resp is False:
                errors_list.append(file.name)

        if errors_list:
            raise serializers.ValidationError(
                {"this files failed": errors_list})

        return HttpResponse(status=200)

    def upload(self, file):
        """Funcion para subir archivos."""

        mf = None  # Objeto mensajes
        resp = True  # variable bandera
        name_file, extension = os.path.splitext(file.name)
        file_match_id = name_file.split("-")[-1]  # obtenemos el ultimo por (-)

        try:
            mf = MatchFile.objects.get(pk=int(file_match_id))
            # lo subimos a Amazon S3
            url = s3_upload_file(file, file.name)
            # generamos la miniatura
            thumb = resize_img(file, 256)
            if thumb:
                name_file_thumb, extension_thumb = os.path.splitext(thumb.name)
                url_thumb = s3_upload_file(thumb, name_file + '-thumb' + extension_thumb)
                remove_file(thumb)
            else:
                url_thumb = ""

            # Actualizamos el modelo mensaje
            mf.file_url = url
            mf.file_preview_url = url_thumb

            s3 = boto3.client('s3')
            # Evaluamos si el archivo se subio a S3
            try:
                s3.head_object(Bucket='linkup-photos', Key=file.name)
            except ClientError as e:
                resp = int(e.response['Error']['Code']) != 404

        except Exception as e:
            logger.error("subir archivo, error general, m_ID: {} - ERROR: {} ".format(file_match_id, e))
            resp = False

        if resp is False:
            mf.uploaded = 5
        else:
            mf.uploaded = 2
        mf.save()

        return resp
