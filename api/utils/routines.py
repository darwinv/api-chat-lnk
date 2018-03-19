"""funciones para llamar a procedimientos almacenados en la basse de datos"""
from django.db import connection

def get_messages_list(flag, user_id, aux_1, aux_2, aux_3):
    try:
        with connection.cursor() as cursor:
            cursor.callproc("SP_MESSAGES_LIST", [flag, user_id, aux_1, aux_2, aux_3])
            result_set = cursor.fetchall()
    finally:
        cursor.close()
    return result_set
