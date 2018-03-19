"""Funciones Varias."""
from api.models import Specialist
from api.models import QueryPlansAcquired
from django.http import Http404


def get_main_specialist(category):
    """Devolver especialista principal segun categoria."""
    try:
        specialist = Specialist.objects.get(type_specialist="m", category_id=category)
        return specialist.id
    except Specialist.DoesNotExist:
        raise Http404


def has_active_plan(client):
    """Verificar si el usuario tiene un plan activo."""
    if QueryPlansAcquired.objects.filter(is_active=True, client_id=client).exists():
        return True
    return False


def has_available_queries(client):
    """Verificar si el usuario tiene consultas disponibles."""
    q = QueryPlansAcquired.objects.get(is_chosen=True, client_id=client)
    return q.available_queries >= 1
