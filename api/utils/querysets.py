"""Funciones Varias."""
from api.models import Specialist
from api.models import QueryPlansAcquired
from django.http import Http404
from django.db.models import F

def get_main_specialist(category):
    """Devolver especialista principal segun categoria."""
    try:
        specialist = Specialist.objects.get(type_specialist="m", category_id=category)
        return specialist.id
    except Specialist.DoesNotExist:
        raise Http404


def has_active_plan(client):
    """Verificar si el usuario tiene un plan activo."""
    if QueryPlansAcquired.objects.filter(is_active=True, queryplansclient__client=client).exists():
        return True
    return False


def has_available_queries(client):
    """Verificar si el usuario tiene consultas disponibles."""
    # import pdb; pdb.set_trace()
    q = QueryPlansAcquired.objects.get(is_chosen=True, queryplansclient__client=client)
    return q.available_queries >= 1

""" Planes de Consultas """
def get_query_set_plan():
    """
    Funcion creada para instancia base de los planes de un cliente
    :return: QuerySet
    """
    return QueryPlansAcquired.objects.values('id', 'is_chosen', 'is_active', 'plan_name',
                                              'query_quantity', 'available_queries',
                                              'validity_months','expiration_date','sale_detail__price')\
            .annotate(price=F('sale_detail__price'))

