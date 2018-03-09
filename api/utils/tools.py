"""
    Archivo creado con la finalidad de crear funciones y clases que permitan trabajar de forma estandar
    el manejo de variables, ejemplo: capitalizar el primer caracter
"""
import datetime
from datetime import datetime as date_time, date, time, timedelta
from django.utils.translation import ugettext_lazy as _

def capitalize(line):
    """
        Funcion creada como herramienta para capitalizar el primer caracter de una cadena
        sin modificar el resto de la cadena
    """

    if len(line) <= 0:
        return ''
    return line[0].upper() + line[1:]

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
    :return: string?
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
        pass
    return None