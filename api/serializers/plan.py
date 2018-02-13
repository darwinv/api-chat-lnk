from rest_framework import serializers
from api.models import QueryPlansAcquired
from api.utils.tools import get_date_by_time 

class PlanDetailSerializer(serializers.ModelSerializer):
    """Serializer del detalle de plan."""
    price = serializers.CharField()

    class Meta:
        """Modelo del especialista y sus campos."""

        model = QueryPlansAcquired
        fields = (
            'plan_name', 'query_quantity', 'available_queries', 'validity_months', 'expiration_date', 'price',
            'is_active')


class ActivePlanSerializer(serializers.ModelSerializer):
    """Serializer del detalle de plan."""

    class Meta:
        """Modelo del especialista y sus campos."""

        model = QueryPlansAcquired
        fields = ('is_active','expiration_date')

    def update(self, instance, validated_data):
        """Redefinido metodo actualizar."""
        instance.is_active = True
        instance.expiration_date = get_date_by_time(instance.validity_months)

        instance.save()
        return instance