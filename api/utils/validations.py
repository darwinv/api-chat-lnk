# from django.http import Http404
from api.models import User, SellerContact

class Operations():
    """
        Clase especial para modular funciones de los usuarios y sus diferentes roles
    """
    def get_id(self, request, user_name_field = 'client_id'):
        """
        Retorna ID de usuario segun su token
        Si es Administrador solicita envio del parametro

        :param request: request from view
        :param user_name_field: nombre del campo a usar para administradores
        :return: Int
        """
        try:
            # validar si es cliente o admin par sacar el id
            if request.user and request.user.role_id == 1:
                # si es admin se necesita sacar el id de body
                if user_name_field in request.data:
                    # Para POST o PUT o DELETE
                    data = request.data
                elif user_name_field in request.query_params:
                    # Para envio por parametros GET
                    data = request.query_params
                else:
                    return None

                return data[user_name_field]
            elif request.user and request.user.role_id != 1:
                # si el token no es de admin, user role 2,3,4 o 5
                return request.user.id
        except Exception as e:
            pass

        return None


def document_exists(type_doc, role, document_number):
    """Verificar si el documento ya existe para ese rol y tipo de documento."""
    return User.objects.filter(document_type=type_doc, role=role,
                               document_number=document_number).exists()


def document_exists_contact(type_doc, document_number):
    """Verificar si el documento ya existe para ese rol y tipo de documento."""
    return SellerContact.objects.filter(document_type=type_doc,
                                        document_number=document_number).exists()


def ruc_exists(residence_country, role, ruc):
    """Verificar si el ruc ya existe para ese rol y nacionalidad."""
    return User.objects.filter(residence_country=residence_country, role=role,
                               ruc=ruc).exists()
