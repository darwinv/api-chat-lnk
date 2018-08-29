"""Estados de cuenta."""
from rest_framework import serializers
from api.models import Specialist, Query
from django.utils.translation import ugettext_lazy as _
from datetime import datetime


class SpecialistAccountSerializer(serializers.ModelSerializer):
    """Serializer de estado de cuenta Especialista"""

    class Meta:
        """Modelo."""

        model = Specialist
        fields = ('id')

    def to_representation(self, obj):
        """To Representation."""
        hoy = datetime.now()  # fecha de hoy
        category_id = self.context["category"]
        # fecha de primer  dia del mes
        primer = datetime(hoy.year, hoy.month, 1, 0, 0, 0)
        # calculó de las consultas absueltas del mes
        month_queries = obj.filter(
            status__range=(4, 5),
            created_at__range=(primer, hoy)).count()
        # calculó de las consultas pendientes por absolver del mes
        month_queries_pending = obj.filter(
            status__range=(1, 3),
            created_at__range=(primer, hoy)).count()
        # calculó el numero de consultas absueltas historico
        queries_absolved = Query.objects.filter(
            status__range=(4, 5), category=category_id).count()

        return {"month_queries_absolved": month_queries,
                "month_queries_pending": month_queries_pending,
                "queries_absolved_category": queries_absolved
                }


class SellerAccountSerializer(serializers.Serializer):
    """Serializer de estado de cuenta Vendedor."""

    def to_representation(self, obj):
        """To Representation."""
        hoy = datetime.now()  # fecha de hoy
        # fecha de primer  dia del mes
        primer = datetime(hoy.year, hoy.month, 1, 0, 0, 0)
        # calculó de los planes vendidos del mes
        month_sold_plans = obj.filter(
            status__range=(2, 3),  # 2 ya pago al menos una parte, 3 se pago completo
            created_at__range=(primer, hoy),
            saledetail__is_billable=True,
            saledetail__product_type=1).count()

        return {"month_sold_plans": month_sold_plans}
