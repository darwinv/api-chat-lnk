from rest_framework.views import APIView
from rest_framework import permissions
from api.models import User
from django.http import Http404
from rest_framework import serializers
from rest_framework.response import Response
from api.api_choices_models import ChoicesAPI
# from rest_framework.generics import ListAPIView


class CheckData(APIView):
    """Chequear si existe un usuario que coincida con la data suministrada."""
    # authentication_classes = []
    permission_classes = [permissions.AllowAny]
    # import pdb; pdb.set_trace()

    def get(self, request):
        """Funcion get."""
        # print("hey")
        # import pdb; pdb.set_trace()
        queryset = User.objects.all()
        # rol debe ser obligatorio
        if 'role' in request.query_params:
            role = request.query_params["role"]
        else:
            raise serializers.ValidationError({'role': ["required"]})

        if 'ruc' in request.query_params:
            queryset = queryset.filter(ruc=request.query_params['ruc'],
                                       role=role)

        if 'email_exact' in request.query_params:
            queryset = queryset.filter(
                email_exact=request.query_params['email_exact'], role=role)

        # debo devolver la  clave del tipo de documento
        # si es proporcionado
        if "document_type" in request.query_params:
            doc_type = return_type_document(
                request.query_params["document_type"])
        # si es suministrado numero de documento tambien debe suministrase su
        # tipo
        if 'document_number' in request.query_params:
            # import pdb; pdb.set_trace()
            number_doc = request.query_params['document_number']
            if 'doc_type' in locals():
                queryset = queryset.filter(document_type=doc_type,
                                           document_number=number_doc,
                                           role=role)
            else:  # si no se da el tipo, devuelvo error
                raise serializers.ValidationError(
                    {'document_number': ["tipo de documento requerido"]})

        if queryset:
            return Response({"ya existe"})
        else:
            raise Http404


def return_type_document(type_document):
    """Regresar tipo de documento."""
    for k, v in ChoicesAPI.user_document_type:
        if type_document.lower() == v.lower():
            return k
