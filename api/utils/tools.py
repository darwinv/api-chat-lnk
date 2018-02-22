## Archivo Tools para crear funciones de sistema generar que seran reutilizadas
# A lo largo del proyecto Linkup
import datetime
from datetime import datetime as date_time, date, time, timedelta
from django.utils.translation import ugettext_lazy as _

def get_date_by_time(validity_months):
    """
    funcion creada para calcular la fecha, segun cantidad en meses dada
    ( 1 mes son 30 dias)
    :param validity_months: Numero entero en meses
    :return: datetime.date
    """
    return datetime.date.today() + datetime.timedelta(validity_months*365/12)


def get_time_message(date_time_message):
    """
    funcion devuelve el tiempo en string de una fecha pasada
    :param date_time_message: Numero entero en meses
    :return: string
    """
    try:
        date_message = date_time_message.date()
        date_time_message = date_time_message
        if date_message == date.today():
            tiempo = time(date_time_message.hour, date_time_message.minute)
            return tiempo
        elif date_message == date.today() - timedelta(days=1):
            return str(_('yesterday'))
        else:
            return date_time.strftime(date_message, '%d/%m/%y')
    except Exception as e:
        return None

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
        else:
            raise None