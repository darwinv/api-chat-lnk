"""Vista de MAtch."""
import os
import boto3
import sys
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
from api.serializers.match import MatchAcceptSerializer, MatchDeclineSerializer
from api.serializers.match import MatchListSpecialistSerializer
from api.serializers.match import MatchListSerializer
from api.serializers.notification import NotificationSpecialistSerializer
from api.serializers.notification import NotificationClientSerializer
from api.serializers.actors import ContactToClientSerializer
from api.permissions import IsAdminOrClient, IsOwnerAndClient
from api.permissions import IsAdminOrSpecialist, IsAdminOnList
from api.models import Match, MatchFile, Sale, QueryPlansAcquired, Client
from api.models import SellerContact, Specialist
from api.utils.tools import s3_upload_file, remove_file, resize_img
from api.logger import manager
from api import pyrebase
from fcm.fcm import Notification
logger = manager.setup_log(__name__)


class MatchListClientView(ListCreateAPIView):
    """Vista Match cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Listado de Matchs."""
        user_id = Operations.get_id(self, request)
        queryset = Match.objects.filter(client_id=user_id)

        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MatchListClientSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MatchListClientSerializer(page, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Metodo para Solicitar Match."""
        # Devolvemos el id del usuario
        data = request.data
        user_id = Operations.get_id(self, request)

        if request.user.role_id == 2:
            data["client"] = user_id
        elif (request.user.role_id == 4 or request.user.role_id == 1) and "client_id" in data and data["client_id"]:
            data["client"] = data["client_id"]
        elif (request.user.role_id == 4 or request.user.role_id == 1) and "email_exact" in data and data["email_exact"]:
            email_exact = data["email_exact"]

            if request.user.role_id == 4:
                user_id = Operations.get_id(self, request)
                data["seller"] = user_id
            else:
                try:
                   data["seller"] = SellerContact.objects.get(email_exact=email_exact).seller.id
                except SellerContact.DoesNotExist:
                    pass

            if "seller" in data and "email_exact" in data:
                serializer_client = ContactToClientSerializer(data=data)
                if serializer_client.is_valid():
                    serializer_client.save()
                    data["client"] = serializer_client.data["client_id"]

                    # categorias firebase para el cliente
                    pyrebase.createCategoriesLisClients(data["client"])
        

        # Cliente que hace match es requerido
        if "client" not in data:
            raise serializers.ValidationError(
                {"client_id": _("required")})


        if 'file' in data:
            if data["file"] is None:
                del data["file"]

        serializer = MatchSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            if 'test' not in sys.argv:
                specialist_id = serializer.data["specialist"]
                # determino el total de consultas pendientes (status 1 o 2)
                # y matchs por responder o pagar
                qset_spec = Specialist.objects.filter(pk=specialist_id)
                dict_pending = NotificationSpecialistSerializer(qset_spec).data
                badge_count = dict_pending["queries_pending"] + dict_pending["match_pending"]
                data_notif_push = {
                    "title": serializer.data['display_name'],
                    "body": serializer.data["subject"],
                    "sub_text": "",
                    "ticker": serializer.data["subject"],
                    "badge": badge_count,
                    "icon": serializer.data['photo'],
                    "queries_pending": dict_pending["queries_pending"],
                    "match_pending": dict_pending["match_pending"],
                    "match_id": serializer.data["id"]
                }
                # envio de notificacion push
                Notification.fcm_send_data(user_id=specialist_id,
                                           data=data_notif_push)

            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class MatchBackendListView(ListCreateAPIView):
    """Vista Match cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOnList, ]


    def list(self, request):
        """Listado de Matchs."""
        queryset = Match.objects.all()
        if 'status' in request.query_params:
            status = request.query_params.getlist('status')
            queryset = queryset.filter(status__in=status)

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


class MatchBackendDetailView(APIView):
    """Vista Match cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOnList]

    def get(self, request, pk):
        """Listado de Matchs."""
        queryset = Match.objects.get(pk=pk)
        serializer = MatchListSerializer(queryset)
        return Response(serializer.data)


class MatchListSpecialistView(ListCreateAPIView):
    """Vista Match cliente."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSpecialist]

    def list(self, request):
        """Listado de Matchs."""
        user_id = Operations.get_id(self, request)
        queryset = Match.objects.filter(specialist=user_id)
        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MatchListSpecialistSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MatchListSpecialistSerializer(page, many=True)
        return Response(serializer.data)


class MatchAcceptView(APIView):
    """Acepta el Match."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSpecialist]

    def put(self, request, pk):
        """Match para un especialista."""
        specialist = Operations.get_id(self, request)
        try:
            match = Match.objects.get(pk=pk, status=1,
                                      specialist=specialist)
        except Match.DoesNotExist:
            raise Http404

        data = request.data
        data["status"] = 2
        serializer = MatchAcceptSerializer(match, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class MatchDeclineView(APIView):
    """Declina el Match."""
    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSpecialist]

    def put(self, request, pk):
        """Redefinido put"""
        specialist = Operations.get_id(self, request)
        try:
            match = Match.objects.get(pk=pk, status=1,
                                      specialist=specialist)
        except Match.DoesNotExist:
            raise Http404

        data = request.data
        data["status"] = 3
        serializer = MatchDeclineSerializer(match, data=data)
        if serializer.is_valid():
            serializer.save()
            if 'test' not in sys.argv:
                client_id = serializer.data["client"]
                qset_client = Client.objects.filter(pk=client_id)
                dict_pending = NotificationClientSerializer(qset_client).data
                badge_count = dict_pending["queries_pending"] + dict_pending["match_pending"]
                data_notif_push = {
                    "title": serializer.data['display_name'],
                    "body": serializer.data["subject"],
                    "sub_text": "",
                    "ticker": serializer.data["declined_motive"],
                    "badge": badge_count,
                    "icon": serializer.data['photo'],
                    "queries_pending": dict_pending["queries_pending"],
                    "match_pending": dict_pending["match_pending"],
                    "match_id": serializer.data["id"]
                }
                # envio de notificacion push
                Notification.fcm_send_data(user_id=client_id,
                                           data=data_notif_push)

            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class MatchUploadFilesView(APIView):
    """Subida de archivos para la consultas."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated]
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
            resp = upload_file(file=file, model_update=MatchFile)
            if resp is False:
                errors_list.append(file.name)

        if errors_list:
            raise serializers.ValidationError(
                {"files_failed": errors_list})

        return HttpResponse(status=200)


class SpecialistMatchUploadFilesView(APIView):
    """Subida de archivos para la consultas."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSpecialist]
    parser_classes = (JSONParser, MultiPartParser)

    def get_object(self, request, pk):
        """Devuelvo la consulta."""
        try:
            obj = Match.objects.get(pk=pk, status=1)
            return obj
        except Match.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Actualiza el match, subiendo archivos."""
        obj_instance = self.get_object(request, pk)
        files = request.FILES.getlist('file')

        if len(files) == 0:
            raise serializers.ValidationError(
                {"file": _("required")})
        errors_list = []
        if files:
            arch = files
        else:
            data = request.data.dict()
            arch = list(data.values())

        for file in arch:
            resp = upload_file(file=file, obj_instance=obj_instance)
            if resp is False:
                errors_list.append(file.name)

        if errors_list:
            raise serializers.ValidationError(
                {"files_failed": errors_list})

        data_match = {}
        data_match["status"] = 2
        data_match["payment_option_specialist"] = 1
        serializer = MatchAcceptSerializer(obj_instance, data=data_match)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class SaleClientUploadFilesView(APIView):
    """Subida de archivos para la consultas."""

    authentication_classes = (OAuth2Authentication,)
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser)

    def get_object(self, request, pk):
        """Devuelvo la consulta."""
        try:
            obj = Sale.objects.get(pk=pk)
            return obj
        except Sale.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Actualiza el match, subiendo archivos."""
        obj_instance = self.get_object(request, pk)
        files = request.FILES.getlist('file')
        if len(files) == 0:
            raise serializers.ValidationError(
                {"file": _("required")})
        errors_list = []
        if files:
            arch = files
        else:
            data = request.data.dict()
            arch = list(data.values())

        for file in arch:
            resp = upload_file(file=file, obj_instance=obj_instance)
            if resp is False:
                errors_list.append(file.name)

        if errors_list:
            raise serializers.ValidationError(
                {"files_failed": errors_list})

        qsdetail = obj_instance.saledetail_set.all()
        # ya se envio el voucher
        QueryPlansAcquired.objects.filter(
            sale_detail__in=qsdetail, status=1).update(status=2)

        Match.objects.filter(
            sale_detail__sale=obj_instance, status=4).update(status=6)

        SellerContact.objects.filter(
            email_exact=obj_instance.client.email_exact).update(type_contact=1)

        return HttpResponse(status=200)

def upload_file(file, model_update=None, obj_instance=None):
    """Funcion para subir archivos."""

    mf = None  # Objeto mensajes
    resp = True  # variable bandera
    name_file, extension = os.path.splitext(file.name)
    file_match_id = name_file.split("-")[-1]  # obtenemos el ultimo por (-)

    try:
        if obj_instance:
            mf = obj_instance
        else:
            mf = model_update.objects.get(pk=int(file_match_id))

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

    if mf:
        mf.save()

    return resp
