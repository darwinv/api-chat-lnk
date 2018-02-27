"""Funciones Varias."""
from api.models import Specialist
from django.http import Http404


def get_main_specialist(self, category):
    """Devolver especialista principal segun categoria."""
    try:
        specialist = Specialist.objects.get(type_specialist="m", category_id=category)
        return specialist.id
    except Specialist.DoesNotExist:
        raise Http404
