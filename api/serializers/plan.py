from rest_framework import serializers
from api.models import QueryPlansAcquired, QueryPlansClient, QueryPlansManage
from api.models import QueryPlans, Client
from api.models import SellerNonBillablePlans
from api.utils.tools import get_date_by_time
from datetime import datetime


class PlanStatusSerializer(serializers.Serializer):

    def to_representation(self, obj):
        """representacion."""
        if obj.exists():
            if obj.filter(is_active=True).exists():
                if obj.filter(queryplansclient__is_chosen=True).exists():
                    return {"code": 4, "message": "Si tiene plan seleccionado"}
                else:
                    return {"code": 3, "message": "No tiene plan seleccionado"}
            else:
                return {"code": 2, "message": "No tiene plan activo"}
        else:
            return {"code": 1, "message": "No tiene plan comprado"}


class PlanDetailSerializer(serializers.ModelSerializer):
    """Serializer del detalle de plan."""
    price = serializers.CharField()
    is_chosen = serializers.SerializerMethodField()

    class Meta:
        """Modelo del especialista y sus campos."""

        model = QueryPlansAcquired
        fields = (
            'plan_name', 'query_quantity', 'available_queries', 'validity_months', 'expiration_date',
            'price','is_active', 'is_chosen')

    def get_is_chosen(self, obj):
        if type(obj) is dict and 'is_chosen' in obj:
            return obj['is_chosen']
        else:
            return obj.is_chosen


class ActivePlanSerializer(serializers.ModelSerializer):
    """Serializer del detalle de plan adquirido."""

    class Meta:
        """Model Plan adquirido."""

        model = QueryPlansAcquired
        fields = ('id', 'plan_name', 'is_active',
                  'query_quantity', 'available_queries',
                  'validity_months', 'expiration_date')
        read_only_fields = ('id', 'plan_name', 'query_quantity',
                            'available_queries', 'validity_months')

    def update(self, instance, validated_data):
        """Redefinido metodo actualizar."""
        is_chosen = self.context['is_chosen']
        client = self.context['client']

        instance.is_active = True
        instance.activation_date = datetime.now().date()
        instance.expiration_date = get_date_by_time(instance.validity_months)
        instance.save()

        query_plan_client = QueryPlansClient.objects.get(client=client,acquired_plan=instance)
        query_plan_client.is_chosen = is_chosen
        query_plan_client.save()

        return instance


class QueryPlansAcquiredSerializer(serializers.ModelSerializer):
    """Plan Adquirido."""
    is_chosen = serializers.SerializerMethodField()
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

    def get_is_chosen(self, obj):
        if type(obj) is dict and 'is_chosen' in obj:
            return obj['is_chosen']
        else:
            try:
                return obj.is_chosen
            except Exception as e:
                return False

class QueryPlansClientSerializer(serializers.ModelSerializer):
    """Plan Adquirido."""

    class Meta:
        """declaracion del modelo y sus campos."""

        model = QueryPlansClient
        fields = ('id','acquired_plan', 'client', 'owner', 'transfer',
                  'share', 'empower',
                  'status', 'is_chosen')

        # extra_kwargs = {
        #         'is_chosen': {'write_only': True},
        #         'is_active': {'write_only': True}
        # }

    def update(self, instance, validated_data):
        """Metodo actualizar redefinido."""
        # traigo todos los demas planes
        plan_list = QueryPlansClient.objects.filter(
            client=instance.client).exclude(pk=instance.id)
        # actualizo el campo is_chosen
        if plan_list.count() > 0:
            plan_list.update(is_chosen=False)

        # Actualizamos el plan actual como elegido
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
    is_chosen = serializers.SerializerMethodField()
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
    def get_is_chosen(self, obj):
        if 'is_chosen' in obj:
            return obj['is_chosen']
        else:
            return False


class QueryPlansTransferSerializer(serializers.ModelSerializer):
    """Plan Adquirido Detail."""

    class Meta:
        """declaracion del modelo y sus campos."""

        model = QueryPlansManage
        fields = ('type_operation','status','acquired_plan','new_acquired_plan',
            'sender','receiver','email_receiver')

    def update(self, instance, validated_data):
        receiver = self.context['client_receiver']

        """Metodo actualizar transferencia de plan."""
        if 'client' in receiver and receiver['client']:
            QueryPlansClient.objects.create(**receiver)

        instance.receiver = validated_data.get(
                               'receiver', instance.receiver)
        instance.status = validated_data.get(
                               'status', instance.status)

        instance.save()
        return instance

    def create(self, validated_data):
        """Transferir plan de consultas"""
        # manage = validated_data.pop('manage')
        receiver = self.context['client_receiver']
        sender = self.context['client_sender']

        instance = QueryPlansManage.objects.create(**validated_data)

        if 'client' in receiver and receiver['client']:
            plan = receiver['acquired_plan']
            plan.is_chosen = False
            plan.save()
            QueryPlansClient.objects.create(**receiver)

        older_owner = QueryPlansClient.objects.get(client=sender['client'],
            acquired_plan=sender['acquired_plan'])
        older_owner.delete()

        return instance


class QueryPlansSerializer(serializers.ModelSerializer):
    """Listado de planes."""

    class Meta:
        """Modelo."""
        model = QueryPlans
        fields = ('id', 'name', 'query_quantity', 'validity_months', 'price')

class QueryPlansShareSerializer(serializers.ModelSerializer):
    """Plan Adquirido Detail."""

    class Meta:
        """declaracion del modelo y sus campos."""

        model = QueryPlansManage
        fields = ('type_operation','status','acquired_plan','new_acquired_plan',
            'sender','receiver','email_receiver', 'count_queries')

    def update(self, instance, validated_data):

        """Metodo actualizar transferencia de plan."""
        count = validated_data.get('count_queries')
        new_acquired_plan = self.process_plan_share(count)

        # Actualizar manejo de plan
        instance.new_acquired_plan = new_acquired_plan

        instance.receiver = validated_data.get(
                               'receiver', instance.receiver)
        instance.status = validated_data.get(
                               'status', instance.status)
        instance.new_acquired_plan = new_acquired_plan
        instance.save()
        return instance

    def process_plan_share(self, count):
        """Procesar compartir plan"""
        receiver = self.context['client_receiver']
        acquired_plan = self.context['acquired_plan']
        plan_manage = self.context['plan_manage']  # Plan de Consulta Anterior

        if plan_manage:
            # Si ya existe plan, se reutiliza el anterior
            new_acquired_plan = plan_manage.new_acquired_plan

            # Aumento la cantidad de queries que comparto
            new_acquired_plan.available_queries = new_acquired_plan.available_queries + count
            new_acquired_plan.query_quantity = new_acquired_plan.query_quantity + count
            new_acquired_plan.save()
        else:
            new_acquired_plan = QueryPlansAcquired()
            new_acquired_plan.available_queries = count
            new_acquired_plan.query_quantity = count
            new_acquired_plan.expiration_date = acquired_plan.expiration_date
            new_acquired_plan.validity_months = acquired_plan.validity_months
            new_acquired_plan.activation_date = acquired_plan.activation_date
            new_acquired_plan.is_active = acquired_plan.is_active
            new_acquired_plan.available_requeries = acquired_plan.available_requeries
            new_acquired_plan.maximum_response_time = acquired_plan.maximum_response_time
            new_acquired_plan.acquired_at = acquired_plan.acquired_at
            new_acquired_plan.query_plans_id = acquired_plan.query_plans_id
            new_acquired_plan.sale_detail_id = acquired_plan.sale_detail_id
            new_acquired_plan.plan_name = acquired_plan.plan_name
            new_acquired_plan.is_chosen = False
            new_acquired_plan.save()

            # Damos los permisos del plan al usuario
            if 'client' in receiver and receiver['client']:
                receiver['acquired_plan'] = new_acquired_plan
                QueryPlansClient.objects.create(**receiver)

        return new_acquired_plan

    def create(self, validated_data):

        """Transferir plan de consultas"""
        acquired_plan = self.context['acquired_plan']
        count = validated_data.get('count_queries')

        new_acquired_plan = self.process_plan_share(count)

        # Actualizo cantidad de consultas
        acquired_plan.available_queries = acquired_plan.available_queries - count
        acquired_plan.save()

        # Crear manejo de plan
        validated_data['new_acquired_plan'] = new_acquired_plan
        instance = QueryPlansManage.objects.create(**validated_data)

        return instance

class QueryPlansEmpowerSerializer(serializers.ModelSerializer):
    """Plan Adquirido Detail."""

    class Meta:
        """declaracion del modelo y sus campos."""

        model = QueryPlansManage
        fields = ('type_operation','status','acquired_plan','new_acquired_plan',
            'sender','receiver','email_receiver')

    def update(self, instance, validated_data):
        receiver = self.context['client_receiver']

        """Metodo actualizar transferencia de plan."""
        if 'client' in receiver and receiver['client']:
            QueryPlansClient.objects.create(**receiver)

        instance.receiver = validated_data.get(
                               'receiver', instance.receiver)
        instance.status = validated_data.get(
                               'status', instance.status)

        instance.save()
        return instance

    def create(self, validated_data):
        """Transferir plan de consultas"""

        receiver = self.context['client_receiver']

        instance = QueryPlansManage.objects.create(**validated_data)

        if 'client' in receiver and receiver['client']:
            QueryPlansClient.objects.create(**receiver)

        return instance

class ClientPlanSerializer(serializers.ModelSerializer):
    """Serializer del detalle de plan."""
    display_name = serializers.SerializerMethodField()
    class Meta:
        """Modelo del especialista y sus campos."""

        model = Client
        fields = ('display_name','photo')

    def get_display_name(self, obj):
        """String Displayname."""

        if obj['type_client'] == 'n':
            display_name = obj['last_name'] + " " + obj['first_name']
        elif obj['type_client'] == 'b':
            display_name = obj['business_name']
        else:
            display_name = ""

        return display_name

class QueryPlansAcquiredSimpleSerializer(serializers.ModelSerializer):
    """Serializer del detalle de plan."""
    class Meta:
        """Modelo del especialista y sus campos."""
        model = QueryPlansAcquired
        fields = ('query_quantity', 'available_queries')


class QueryPlansManageSerializer(serializers.ModelSerializer):
    """Serializer del detalle de plan."""
    receiver = serializers.SerializerMethodField()
    new_acquired_plan = serializers.SerializerMethodField()
    class Meta:
        """Modelo del especialista y sus campos."""

        model = QueryPlansManage
        fields = ('status',
            'email_receiver', 'type_operation',
            'receiver','new_acquired_plan')

    def get_receiver(self, obj):
        """Cliente"""
        if obj['receiver']:
            return ClientPlanSerializer(obj).data
        return None

    def get_new_acquired_plan(self, obj):
        """plan de consulta"""
        if obj['new_acquired_plan']:
            return QueryPlansAcquiredSimpleSerializer(obj).data
        return None


class PlansNonBillableSerializer(serializers.ModelSerializer):

    class Meta:
        """Modelo."""
        model = SellerNonBillablePlans
        fields = ('seller', 'query_plans', 'quantity',
                  'number_month')

    def to_representation(self, instance):
        """representation."""
        data = {
            "id": instance.id,
            "name": instance.query_plans.name,
            "query_quantity": instance.query_plans.query_quantity,
            "validity_months": instance.query_plans.validity_months,
            "price": instance.query_plans.price
        }
        return data
