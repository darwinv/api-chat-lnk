"""Estados de cuenta."""
from rest_framework import serializers
from api.models import Specialist, Query, SellerContact, ParameterSeller
from api.models import SellerNonBillablePlans, Declinator, QueryPlansAcquired
from api.models import Match
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta, date
from django.db.models import Count, Sum, Q
from api.serializers.plan import QueryPlansAcquiredSimpleSerializer


class SpecialistAccountSerializer(serializers.ModelSerializer):
    """Serializer de estado de cuenta Especialista"""

    class Meta:
        """Modelo."""

        model = Specialist
        fields = ('id')

    def to_representation(self, obj):
        """To Representation."""

        category_id = self.context["category"]
        specialist = self.context["specialist"]

        # fecha de hoy
        hoy = datetime.now()
        # fecha de primer  dia del mes
        primer = datetime(hoy.year, hoy.month, 1, 0, 0, 0)

        # consultas declinadas del mes
        # queries_declined = Declinator.objects.filter(
        #     specialist=specialist,
        #     query__created_at__range=(primer, hoy)).count()

        # calculó de las consultas absueltas del mes
        queries_main_absolved = obj.filter(
            status__range=(4, 5),
            created_at__range=(primer, hoy)).count()
        # calculó de las consultas pendientes por absolver del mes
        queries_main_pending = obj.filter(
            status__range=(1, 3),
            created_at__range=(primer, hoy)).count()

        # calculó el numero de consultas absueltas mensual por especialidad
        queries_category_absolved = Query.objects.filter(
            status__range=(4, 5), category=category_id,
            created_at__range=(primer, hoy)).count()

        # calculó el numero de consultas pendientes mensual por especialidad
        queries_category_pending = Query.objects.filter(
            status__range=(1, 3), category=category_id,
            created_at__range=(primer, hoy)).count()

        match_total = Match.objects.filter(specialist=specialist,
                                            created_at__range=(primer, hoy)).count()
        match_accepted = Match.objects.filter(specialist=specialist, status=5,
                                            created_at__range=(primer, hoy)).count()
        match_declined = Match.objects.filter(specialist=specialist, status=3,
                                            created_at__range=(primer, hoy)).count()

        # consultas por especialista
        # queries_specialist = obj.filter(status__range=(4, 5)).count()
        queries_asociate_total = queries_category_absolved+queries_category_pending - queries_main_absolved-queries_main_pending
        return {
                "queries_category_total": queries_category_absolved+queries_category_pending,
                "queries_category_absolved": queries_category_absolved,
                "queries_category_pending": queries_category_pending,

                "queries_main_total": queries_main_absolved+queries_main_pending,
                "queries_main_absolved": queries_main_absolved,
                "queries_main_pending": queries_main_pending,

                "queries_asociate_total": queries_asociate_total,
                "queries_asociate_absolved": queries_category_absolved - queries_main_absolved,
                "queries_asociate_pending": queries_category_pending - queries_main_pending,

                "match_total": match_total,
                "match_accepted": match_accepted,
                "match_declined": match_declined,
                }

class SpecialistHistoricAccountSerializer(serializers.ModelSerializer):
    """Serializer de estado de cuenta Especialista"""

    class Meta:
        """Modelo."""

        model = Specialist
        fields = ('id')

    def to_representation(self, obj):
        """To Representation."""
        category_id = self.context["category"]
        queries_main_absolved = obj.filter(
            status__range=(4, 5)).count()

        # calculó el numero de consultas absueltas mensual por especialidad
        queries_category_absolved = Query.objects.filter(
            status__range=(4, 5), category=category_id).count()

        return {
                "queries_category_absolved": queries_category_absolved,
                "queries_main_absolved": queries_main_absolved,
                "queries_asociate_absolved": queries_category_absolved - queries_main_absolved
                }

class SpecialistAsociateAccountSerializer(serializers.ModelSerializer):
    """Serializer de estado de cuenta Especialista Asociado"""

    class Meta:
        """Modelo."""

        model = Specialist
        fields = ('id')

    def to_representation(self, obj):
        """To Representation."""
        # fecha de hoy
        hoy = datetime.now()
        # fecha de primer  dia del mes
        primer = datetime(hoy.year, hoy.month, 1, 0, 0, 0)

        # calculó de las consultas absueltas del mes
        queries_asociate_absolved = obj.filter(
            status__range=(4, 5),
            created_at__range=(primer, hoy)).count()

        # calculó de las consultas pendientes por absolver del mes
        queries_asociate_pending = obj.filter(
            status__range=(1, 3),
            created_at__range=(primer, hoy)).count()

        return {
                "queries_asociate_total": queries_asociate_absolved + queries_asociate_pending,
                "queries_asociate_absolved": queries_asociate_absolved,
                "queries_asociate_pending": queries_asociate_pending
                }

class SpecialistAsociateHistoricAccountSerializer(serializers.ModelSerializer):
    """Serializer de estado de cuenta Especialista Asociado"""

    class Meta:
        """Modelo."""

        model = Specialist
        fields = ('id')

    def to_representation(self, obj):
        """To Representation."""
        specialist = self.context["specialist"]

        queries_asociate_absolved = obj.filter(
            status__range=(4, 5)).count()

        # calculó el numero de consultas absueltas mensual por especialidad
        queries_asociate_declinated = Declinator.objects.filter(
            specialist=specialist).count()

        return {
                "queries_asociate_total": queries_asociate_absolved + queries_asociate_declinated,
                "queries_asociate_absolved": queries_asociate_absolved,
                "queries_asociate_declinated": queries_asociate_declinated
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

        client_id = self.context["client"]

        end = datetime.now()
        new_end = end + timedelta(days=1)
        start = date(end.year, end.month, 1)
        plan = obj.filter(activation_date__range=(start, new_end))

        serializers_plans = QueryPlansAcquiredSimpleSerializer(plan, many=True)

        match_acquired = Match.objects.filter(client=client_id, created_at__range=(start, new_end)).count()
        match_absolved = Match.objects.filter(client=client_id, status=5, created_at__range=(start, new_end)).count()
        match_declined = Match.objects.filter(client=client_id, status=3, created_at__range=(start, new_end)).count()

        return {
                "plans": serializers_plans.data,
                "match_acquired": match_acquired,
                "match_absolved": match_absolved,
                "match_declined": match_declined
                }


class ClientAccountHistoricSerializer(serializers.Serializer):
    """Serializer de estado de cuenta de Cliente."""

    def to_representation(self, obj):
        """Representacion."""

        client_id = self.context["client"]
        # calculó de las consultas adquiridas
        # import pdb; pdb.set_trace()
        queries_client = obj.aggregate(query_quantity=Sum('query_quantity'),
                             available_queries=Sum('available_queries'),
                             queries_to_pay=Sum('queries_to_pay'))

        queries_acquired = queries_client["query_quantity"] if queries_client["query_quantity"] else 0
        queries_available = queries_client["available_queries"] if queries_client["available_queries"] else 0
        queries_to_pay = queries_client["queries_to_pay"] if queries_client["queries_to_pay"] else 0

        queries_made = queries_acquired - queries_available - queries_to_pay

        match_acquired = Match.objects.filter(client=client_id).count()
        match_absolved = Match.objects.filter(client=client_id, status=5).count()
        match_declined = Match.objects.filter(client=client_id, status=3).count()
        return {
                "queries_acquired": queries_acquired,
                "queries_made": queries_made,
                "queries_available": queries_available,
                "match_acquired": match_acquired,
                "match_absolved": match_absolved,
                "match_declined": match_declined
                }

class SellerAccountSerializer(serializers.Serializer):
    """Serializer de estado de cuenta Vendedor."""

    def to_representation(self, obj):
        """To Representation."""
        seller = self.context["seller"]

        # fecha de hoy
        to_date = datetime.now()
        # fecha de primer  dia del mes
        from_date = datetime(to_date.year, to_date.month, 1, 0, 0, 0)


        # clientes nuevos que ya pagaron en este mes
        new_clients = SellerContact.objects.filter(seller=seller,
                                                   type_contact=3,
                                                   created_at__range=(from_date, to_date)).count()
        # contactos nuevos registrados
        contacts = SellerContact.objects.filter(seller=seller,
                                                created_at__range=(from_date, to_date)).count()
        # planes promocionales entregados en el mes
        promotional_plans = obj.filter(saledetail__product_type=1,
                                       saledetail__is_billable=False,
                                       created_at__range=(from_date, to_date)).count()

        qs = obj.filter(saledetail__product_type=1,
                        saledetail__is_billable=True,
                        created_at__range=(from_date, to_date),
                        status__range=(2, 3)).values('client_id')
        # Cantidad de personas  que compraron este mes
        people_purchase = qs.annotate(client_count=Count('client_id')).count()
        # instancia parametro de vendedor
        try:
            seller_param = ParameterSeller.objects.get(seller=seller,
                                                       number_month=to_date.month,
                                                       number_year=to_date.year)
            contacts_goal = seller_param.contacts_goal
            new_clients_goal = seller_param.new_clients_goal
            people_purchase_goal = seller_param.people_purchase_goal
        except ParameterSeller.DoesNotExist:
            contacts_goal = new_clients_goal = people_purchase_goal = 0
        # suma de promocionales disponibles
        quant_dic = SellerNonBillablePlans.objects.filter(
            number_month=to_date.month, number_year=to_date.year, seller=seller).aggregate(Sum('quantity'))
        # todos los promocionales de ese mes

        if quant_dic["quantity__sum"]:
            # sumo los promocionales que me quedan con los promocionales entregados
            all_promo = quant_dic["quantity__sum"] + promotional_plans
        else:
            all_promo = 0 + promotional_plans

        return {
                    "month_new_clients_goal": new_clients_goal,
                    "month_clients": new_clients,

                    "month_contacts_goal": contacts_goal,
                    "month_contacts": contacts,

                    "month_people_purchase_goal": people_purchase_goal,
                    "month_people_purchase": people_purchase,

                    "month_all_promotionals": all_promo,
                    "month_promotionals": promotional_plans
                }

class SellerAccountHistoricSerializer(serializers.Serializer):
    """Serializer de estado de cuenta Vendedor."""

    def to_representation(self, obj):
        """To Representation."""
        seller = self.context["seller"]

        # clientes nuevos que ya pagaron en este mes
        new_clients = SellerContact.objects.filter(seller=seller,
                                                   type_contact=3).count()
        # contactos nuevos registrados
        contacts = SellerContact.objects.filter(seller=seller).count()


        qs = obj.filter(saledetail__product_type=1,
                        saledetail__is_billable=True,
                        status__range=(2, 3)).values('client_id')
        # Cantidad de personas  que compraron este mes
        people_purchase = qs.annotate(client_count=Count('client_id')).count()


        return {
                    "total_clients": new_clients,
                    "total_contacts": contacts,
                    "total_people_purchase": people_purchase
                }

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

        if queries_sold["queries"] is None:
            queries_sold["queries"] = 0

        if all_queries_sold["queries"] is None:
            all_queries_sold["queries"] = 0

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
