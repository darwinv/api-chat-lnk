"""Estados de cuenta."""
from rest_framework import serializers
from api.models import Specialist, Query, SellerContact, ParameterSeller
from api.models import SellerNonBillablePlans, Declinator
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from django.db.models import Count, Sum, Q


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
        specialist = self.context["specialist"]
        # fecha de primer  dia del mes
        primer = datetime(hoy.year, hoy.month, 1, 0, 0, 0)
        # consultas declinadas del mes
        month_queries_declined = Declinator.objects.filter(
            specialist=specialist,
            query__created_at__range=(primer, hoy)).count()
        # calculó de las consultas absueltas del mes
        month_queries = obj.filter(
            status__range=(4, 5),
            created_at__range=(primer, hoy)).count()
        # calculó de las consultas pendientes por absolver del mes
        month_queries_pending = obj.filter(
            status__range=(1, 3),
            created_at__range=(primer, hoy)).count()
        # calculó el numero de consultas absueltas historico por especialidad
        queries_absolved = Query.objects.filter(
            status__range=(4, 5), category=category_id).count()
        # consultas por especialista
        # queries_specialist = obj.filter(status__range=(4, 5)).count()

        return {"month_queries_absolved": month_queries,
                "month_queries_pending": month_queries_pending,
                "queries_absolved_category": queries_absolved,
                "month_queries_declined": month_queries_declined,
                }


class SpecialistFooterSerializer(serializers.ModelSerializer):
    """Serializer para datos del footer del especialista."""

    class Meta:
        """Modelo."""

        model = Specialist
        fields = ('id')

    def to_representation(self, obj):
        hoy = datetime.now()  # fecha de hoy
        # fecha de primer  dia del mes
        primer = datetime(hoy.year, hoy.month, 1, 0, 0, 0)
        # calculó de las consultas absueltas del mes
        month_queries = obj.filter(status__range=(4, 5),
                                   created_at__range=(primer, hoy)).count()

        queries_absolved = obj.filter(status__range=(4, 5)).count()

        return {"month_queries_absolved": month_queries,
                "queries_absolved": queries_absolved}


class ClientAccountSerializer(serializers.Serializer):
    """Serializer de estado de cuenta de Cliente."""

    def to_representation(self, obj):
        """Representacion."""

        client = self.context["client"]
        # calculó de las consultas adquiridas
        resp = obj.aggregate(queries=Sum('acquired_plan__query_quantity'),
                             av_queries=Sum('acquired_plan__available_queries'))
        # calculó de las consultas absueltas
        queries = Query.objects.filter(client=client,
                                       status__range=(4, 5)).count()

        # calculó de las consultas pendientes
        queries_pending = Query.objects.filter(client=client,
                                               status__range=(1, 3)).count()

        return {"queries_acquired": resp["queries"],
                "queries_absolved": queries,
                "queries_pending": queries_pending,
                "available_queries": resp["av_queries"]
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
                                                       number_month=hoy.month,
                                                       number_year=hoy.year)
            contacts_goal = seller_param.contacts_goal
            new_clients_goal = seller_param.new_clients_goal
            people_purchase_goal = seller_param.people_purchase_goal
        except ParameterSeller.DoesNotExist:
            contacts_goal = new_clients_goal = people_purchase_goal = None
        # suma de promocionales disponibles
        quant_dic = SellerNonBillablePlans.objects.filter(
            number_month=hoy.month, number_year=hoy.year, seller=seller).aggregate(Sum('quantity'))
        # todos los promocionales de ese mes

        if quant_dic["quantity__sum"]:
            all_promo = quant_dic["quantity__sum"] + promotional_plans
        else:
            all_promo = 0 + promotional_plans

        return {"month_clients": new_clients,
                "month_contacts": contacts,
                "month_promotionals": promotional_plans,
                "month_people_purchase": people_purchase,
                "month_people_purchase_goal": people_purchase_goal,
                "month_contacts_goal": contacts_goal,
                "month_new_clients_goal": new_clients_goal,
                "month_all_promotionals": all_promo}


class SellerAccountBackendSerializer(serializers.Serializer):
    """Serializer de estado de cuenta Vendedor."""

    def to_representation(self, obj):
        """To Representation."""
        seller = self.context["seller"]
        hoy = datetime.now()  # fecha de hoy
        # fecha de primer  dia del mes
        primer = datetime(hoy.year, hoy.month, 1, 0, 0, 0)
        # planes promocionales entregados en el mes
        promotional_plans = obj.filter(saledetail__product_type=1,
                                       saledetail__is_billable=False,
                                       created_at__range=(primer, hoy)).count()

        promotional_history = obj.filter(saledetail__product_type=1,
                                         saledetail__is_billable=False,
                                         ).count()
        # suma de promocionales disponibles
        quant_dic = SellerNonBillablePlans.objects.filter(
            number_month=hoy.month, number_year=hoy.year, seller=seller).aggregate(Sum('quantity'))
        # todos los promocionales de ese mes

        if quant_dic["quantity__sum"]:
            all_promo = quant_dic["quantity__sum"] + promotional_plans
        else:
            all_promo = 0 + promotional_plans

        # planes vendidos en este mes
        plans_sold = obj.filter(saledetail__product_type=1,
                                saledetail__is_billable=True,
                                created_at__range=(primer, hoy),
                                status__range=(2, 3)).count()
        # planes vendidos todo los tiempos
        all_plans_sold = obj.filter(saledetail__product_type=1,
                                    saledetail__is_billable=True,
                                    status__range=(2, 3)).count()
        # consultas vendidas historico
        queries_sold = obj.filter(saledetail__product_type=1,
                                  saledetail__is_billable=True,
                                  created_at__range=(primer, hoy),
                                  status__range=(2, 3)).aggregate(queries=Sum('saledetail__queryplansacquired__query_quantity'))
        # consultas vendidas equivalentes historico
        all_queries_sold = obj.filter(saledetail__product_type=1,
                                      saledetail__is_billable=True,
                                      status__range=(2, 3)).aggregate(queries=Sum('saledetail__queryplansacquired__query_quantity'))

        # instancia parametro de vendedor
        try:
            seller_param = ParameterSeller.objects.get(seller=seller,
                                                       number_month=hoy.month,
                                                       number_year=hoy.year)
            new_clients_goal = seller_param.new_clients_goal
        except ParameterSeller.DoesNotExist:
            new_clients_goal = 0

        if not queries_sold["queries"]:
            queries_sold["queries"] = 0

        return {
                    "month_sold_plans": plans_sold,
                    "month_sold_queries": queries_sold["queries"],

                    "sold_plans": all_plans_sold,
                    "sold_queries": all_queries_sold["queries"],

                    "month_new_clients_goal": new_clients_goal,
                    "month_all_promotionals": all_promo,

                    "month_promotionals": promotional_plans,
                    "promotionals": promotional_history
                }


class SellerFooterSerializer(serializers.Serializer):
    """Serializer para datos del footer del vendedor."""

    def to_representation(self, obj):
        """To Representation."""
        seller = self.context["seller"]
        hoy = datetime.now()  # fecha de hoy
        # fecha de primer  dia del mes
        primer = datetime(hoy.year, hoy.month, 1, 0, 0, 0)
        # planes promocionales entregados en el mes
        promotional_plans = obj.filter(saledetail__product_type=1,
                                       saledetail__is_billable=False,
                                       created_at__range=(primer, hoy)).count()
        # contactos no efectivos
        contacts_not_effective = SellerContact.objects.filter(
            seller=seller, type_contact=2,
            created_at__range=(primer, hoy)).count()
        # contactos efectivos
        contacts_effective = SellerContact.objects.filter(
            Q(type_contact=1) | Q(type_contact=3),
            seller=seller, created_at__range=(primer, hoy)).count()

        return {"month_promotionals": promotional_plans,
                "month_not_effective": contacts_not_effective,
                "month_effective": contacts_effective}




# SELECT
# Sum(api_queryplansacquired.query_quantity) AS consultas_adquiridas
# FROM
# api_queryplansclient
# Inner Join api_queryplansacquired ON api_queryplansclient.acquired_plan_id = api_queryplansacquired.id
# WHERE
# api_queryplansclient.client_id =  4

# SELECT
# SUM(api_queryplansacquired.query_quantity) AS consultas_vendidas
# FROM
# api_saledetail
# Inner Join api_sale ON api_saledetail.sale_id = api_sale.id
# Inner Join api_queryplansacquired ON api_queryplansacquired.sale_detail_id = api_saledetail.id
# WHERE
# api_saledetail.is_billable =  1 AND
# api_sale.seller_id =  6 AND
# api_saledetail.product_type_id =  1
# api_sale.status between 2 3
# api_sale.created_at
