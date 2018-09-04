"""Estados de cuenta."""
from rest_framework import serializers
from api.models import Specialist, Query, SellerContact, ParameterSeller
from api.models import SellerNonBillablePlans
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from django.db.models import Count, Sum


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
        seller = self.context["seller"]
        hoy = datetime.now()  # fecha de hoy
        # fecha de primer  dia del mes
        primer = datetime(hoy.year, hoy.month, 1, 0, 0, 0)
        # clientes nuevos que ya pagaron en este mes
        new_clients = SellerContact.objects.filter(seller=seller,
                                                   type_contact=3,
                                                   created_at__range=(primer, hoy)).count()
        # contactos nuevos registrados
        contacts = SellerContact.objects.filter(seller=seller,
                                                created_at__range=(primer, hoy)).count()
        # planes promocionales entregados en el mes
        promotional_plans = obj.filter(saledetail__product_type=1,
                                       saledetail__is_billable=False,
                                       created_at__range=(primer, hoy)).count()

        qs = obj.filter(saledetail__product_type=1,
                        saledetail__is_billable=True,
                        created_at__range=(primer, hoy),
                        status__range=(2, 3)).values('client_id')
        # Cantidad de personas  que compraron este mes
        people_purchase = qs.annotate(client_count=Count('client_id')).count()
        # instancia parametro de vendedor
        try:
            seller_param = ParameterSeller.objects.get(seller=seller,
                                                       number_month=hoy.month)
            contacts_goal = seller_param.contacts_goal
            new_clients_goal = seller_param.new_clients_goal
            people_purchase_goal = seller_param.people_purchase_goal
        except ParameterSeller.DoesNotExist:
            contacts_goal = new_clients_goal = None
        # suma de promocionales disponibles
        quant_dic = SellerNonBillablePlans.objects.filter(
            number_month=hoy.month, seller=seller).aggregate(Sum('quantity'))
        # todos los promocionales de ese mes
        all_promo = quant_dic["quantity__sum"] + promotional_plans

        return {"month_clients": new_clients,
                "month_contacts": contacts,
                "month_promotionals": promotional_plans,
                "month_people_purchase": people_purchase,
                "month_people_purchase_goal": people_purchase_goal,
                "month_contacts_goal": contacts_goal,
                "month_new_clients_goal": new_clients_goal,
                "month_all_promotionals": all_promo}



# Cantidad de personas que me compraron este mes
# SELECT
# DISTINCT api_sale.client_id
# FROM
# api_sale
# Inner Join api_saledetail ON api_saledetail.sale_id = api_sale.id
# WHERE
# api_sale.seller_id =  6 AND
# api_saledetail.product_type_id =  1 AND
# api_saledetail.is_billable =  1 AND
# api_sale.created_at BETWEEN  '2018-08-01' AND
