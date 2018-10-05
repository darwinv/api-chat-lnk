"""Vista de MAtch."""
import os
import boto3
from django.http import Http404, HttpResponse
from botocore.exceptions import ClientError
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status, permissions
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from api.utils.validations import Operations
from api.serializers.match import MatchSerializer
from api.permissions import IsAdminOrClient, IsOwnerAndClient
from api.models import Match, MatchFile
from api.utils.tools import s3_upload_file, remove_file, resize_img
from api.logger import manager
logger = manager.setup_log(__name__)


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

        return resp
