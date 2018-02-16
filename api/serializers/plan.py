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
            'plan_name', 'query_quantity', 'available_queries', 'validity_months', 'expiration_date',
            'price','is_active', 'is_chosen')


class ActivePlanSerializer(serializers.ModelSerializer):
    """Serializer del detalle de plan."""

    class Meta:
        """Modelo del especialista y sus campos."""

        model = QueryPlansAcquired
        fields = ('is_active','expiration_date')

    def update(self, instance, validated_data):
        """Redefinido metodo actualizar."""
        is_chosen = self.context['is_chosen']
        
        instance.is_active = True
        instance.is_chosen = is_chosen
        instance.expiration_date = get_date_by_time(instance.validity_months)

        instance.save()
        return instance

class QueryPlansAcquiredSerializer(serializers.ModelSerializer):
#    expiration_date = models.DateField(null=True)
#    validity_months = models.PositiveIntegerField()
#    available_queries = models.PositiveIntegerField()
#    query_quantity = models.PositiveIntegerField()
#    activation_date = models.DateField(null=True)
#    is_active = models.BooleanField(default=False)
#    is_chosen = models.BooleanField(default=False)
#    available_requeries = models.PositiveIntegerField()
#    maximum_response_time = models.PositiveIntegerField()  # En Horas
#    acquired_at = models.DateTimeField(auto_now_add=True)
    plan_name = serializers.CharField(required=True)
    cliente = serializers.CharField(required=True)
    is_chosen = serializers.BooleanField(required=True)
    is_active = serializers.BooleanField(required=True)
    query_quantity = serializers.IntegerField(required=True)
    available_queries = serializers.IntegerField(required=True)
    validity_months = serializers.IntegerField(required=True)
    expiration_date = serializers.CharField(required=True)

#    cliente = models.ForeignKey(Client, on_delete=models.PROTECT)
#    query_plans = models.ForeignKey(QueryPlans, on_delete=models.PROTECT)
#    sale_detail = models.ForeignKey(SaleDetail, on_delete=models.PROTECT)

    class Meta:
        """declaracion del modelo y sus campos."""
        model = QueryPlansAcquired
        fields = ('id', 'plan_name','cliente','is_chosen','is_active','query_quantity',
                    'available_queries','validity_months','expiration_date')