from rest_framework import serializers
from api.models import QueryPlansAcquired
from api.utils.tools import get_date_by_time
from datetime import datetime

class PlanDetailSerializer(serializers.ModelSerializer):
    """Serializer del detalle de plan."""
    price = serializers.CharField()
    class Meta:
        """Modelo del especialista y sus campos."""

        model = QueryPlansAcquired
        fields = (
            'plan_name', 'query_quantity', 'available_queries', 'validity_months', 'expiration_date',
            'price','is_active', 'is_chosen')


class ActivePlanSerializer(serializers.ModelSerializer):
    """Serializer del detalle de plan adquirido."""

    class Meta:
        """Model Plan adquirido."""

        model = QueryPlansAcquired
        fields = ('id', 'plan_name', 'is_chosen', 'is_active',
                  'query_quantity', 'available_queries',
                  'validity_months', 'expiration_date')
        read_only_fields = ('id', 'plan_name', 'query_quantity',
                            'available_queries', 'validity_months')

    def update(self, instance, validated_data):
        """Redefinido metodo actualizar."""
        is_chosen = self.context['is_chosen']

        instance.is_active = True
        instance.is_chosen = is_chosen
        instance.activation_date = datetime.now().date()
        instance.expiration_date = get_date_by_time(instance.validity_months)

        instance.save()
        return instance


class QueryPlansAcquiredSerializer(serializers.ModelSerializer):
    """Plan Adquirido."""

    class Meta:
        """declaracion del modelo y sus campos."""

        model = QueryPlansAcquired
        fields = ('id', 'plan_name', 'is_chosen', 'is_active',
                  'validity_months', 'query_quantity',
                  'available_queries', 'expiration_date')

        # extra_kwargs = {
        #         'is_chosen': {'write_only': True},
        #         'is_active': {'write_only': True}
        # }

    def update(self, instance, validated_data):
        """Metodo actualizar redefinido."""
        instance.is_chosen = validated_data.get(
                               'is_chosen', instance.is_chosen)
        instance.save()
        return instance

class QueryPlansAcquiredDetailSerializer(serializers.ModelSerializer):
    """Plan Adquirido Detail."""
    transfer = serializers.SerializerMethodField()
    share = serializers.SerializerMethodField()
    empower = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        """declaracion del modelo y sus campos."""

        model = QueryPlansAcquired
        fields = ('id', 'plan_name', 'is_chosen', 'is_active',
                  'validity_months', 'query_quantity',
                  'available_queries', 'expiration_date', 'transfer',
                  'share', 'empower', 'owner')

    def get_transfer(self, obj):
        if 'queryplansclient__transfer' in obj:
            return obj['queryplansclient__transfer']
        else:
            return False
    def get_share(self, obj):
        if 'queryplansclient__share' in obj:
            return obj['queryplansclient__share']
        else:
            return False
    def get_empower(self, obj):
        if 'queryplansclient__empower' in obj:
            return obj['queryplansclient__empower']
        else:
            return False
    def get_owner(self, obj):
        if 'queryplansclient__owner' in obj:
            return obj['queryplansclient__owner']
        else:
            return False