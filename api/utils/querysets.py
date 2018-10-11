"""Funciones Varias."""
from api.models import Specialist
from api.models import QueryPlansAcquired, MonthlyFee, Query
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
    try:
        q = QueryPlansAcquired.objects.get(queryplansclient__is_chosen=True, queryplansclient__client=client)
        return q.available_queries >= 1
    except QueryPlansAcquired.DoesNotExist:
        return False



""" Planes de Consultas """
def get_query_set_plan():
    """
    Funcion creada para instancia base de los planes de un cliente
    :return: QuerySet
    """
    return QueryPlansAcquired.objects.values('id', 'is_active', 'plan_name',
                                              'query_quantity', 'available_queries',
                                              'validity_months','expiration_date','sale_detail__price')\
            .annotate(price=F('sale_detail__price'), is_chosen=F('queryplansclient__is_chosen'))


def get_next_fee_to_pay(sale):
    """ Cuotas de Venta """
    """
    Funcion creada para traer la proxima cuota a pagar
    :return: QuerySet
    """
    try:
        return MonthlyFee.objects.filter(sale=sale, status=1).order_by('pay_before')[0]
    except IndexError:
        return None


def get_queries_pending_to_solve(specialist, client):
    """ Consultas pendientes por resolver """
    """
    Devuelve el numero total de consultas en estado 1 o 2.
    :return: Int
    """
    qs = Query.objects.filter(status__range=(1, 2),
                              specialist=specialist, client=client)
    pending = qs.count()
    return pending
