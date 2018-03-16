"""funciones para llamar a procedimientos almacenados en la basse de datos"""
from django.db import connection

def get_messages_list(flag, client_id, specialist_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc("SP_MESSAGES_LIST", [flag, client_id, specialist_id])
            result_set = cursor.fetchall()
    finally:
        cursor.close()
    return result_set
