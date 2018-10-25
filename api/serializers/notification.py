"""Notification Serializer."""
from rest_framework import serializers
from api.models import Query


class NotificationClientSerializer(serializers.Serializer):
    """Serializer de data pendiente."""
    def to_representation(self, queryset):
        queries_pending = queryset.filter(query__status__range=(3, 4)).count()
        match_pending = queryset.filter(match__status=4).count()

        return {
                "queries_pending": queries_pending,
                "match_pending": match_pending
                }


class NotificationSpecialistSerializer(serializers.Serializer):
    """Serializer de data pendiente."""
    def to_representation(self, queryset):
        specialist = queryset.get()
        if specialist.type_specialist == 'm':
            queries_pending = Query.objects.filter(
                status__range=(1, 2), category=specialist.category).count()

            match_pending = queryset.filter(
                match__status__range=(1, 2)).count()
            return {"queries_pending": queries_pending,
                    "match_pending": match_pending}
        else:
            queries_pending = queryset.filter(
                query__status__range=(1, 2)).count()

            return {"queries_pending": queries_pending,
                    "match_pending": 0}
