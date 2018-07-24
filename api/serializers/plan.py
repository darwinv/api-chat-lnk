from rest_framework import serializers
from api.models import QueryPlansAcquired, QueryPlansClient, QueryPlansManage
from api.models import QueryPlans, Client
from api.models import SellerNonBillablePlans
from api.utils.tools import get_date_by_time
from datetime import datetime


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


class QueryPlansTransfer(serializers.ModelSerializer):
    """Plan Adquirido Detail."""

    class Meta:
        """declaracion del modelo y sus campos."""

        model = QueryPlansManage
        fields = ('type_operation','status','acquired_plan','new_acquired_plan',
            'sender','receiver','email_receiver')

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
        fields = ('name', 'query_quantity', 'validity_months', 'price')

class QueryPlansShare(serializers.ModelSerializer):
    """Plan Adquirido Detail."""

    class Meta:
        """declaracion del modelo y sus campos."""

        model = QueryPlansManage
        fields = ('type_operation','status','acquired_plan','new_acquired_plan',
            'sender','receiver','email_receiver')

    def create(self, validated_data):
        """Transferir plan de consultas"""

        count = self.context['count']
        receiver = self.context['client_receiver']
        acquired_plan = self.context['acquired_plan']

        query_plans = QueryPlansAcquired()
        query_plans.available_queries = count
        query_plans.query_quantity = count
        query_plans.expiration_date = acquired_plan.expiration_date
        query_plans.validity_months = acquired_plan.validity_months
        query_plans.activation_date = acquired_plan.activation_date
        query_plans.is_active = acquired_plan.is_active
        query_plans.available_requeries = acquired_plan.available_requeries
        query_plans.maximum_response_time = acquired_plan.maximum_response_time
        query_plans.acquired_at = acquired_plan.acquired_at
        query_plans.query_plans_id = acquired_plan.query_plans_id
        query_plans.sale_detail_id = acquired_plan.sale_detail_id
        query_plans.plan_name = acquired_plan.plan_name
        query_plans.is_chosen = False
        query_plans.save()
        
        acquired_plan.available_queries = acquired_plan.available_queries - count
        acquired_plan.save()

        validated_data['new_acquired_plan'] = query_plans
        receiver['acquired_plan'] = query_plans

        instance = QueryPlansManage.objects.create(**validated_data)

        if 'client' in receiver and receiver['client']:
            QueryPlansClient.objects.create(**receiver)

        return instance

class QueryPlansEmpower(serializers.ModelSerializer):
    """Plan Adquirido Detail."""

    class Meta:
        """declaracion del modelo y sus campos."""

        model = QueryPlansManage
        fields = ('type_operation','status','acquired_plan','new_acquired_plan',
            'sender','receiver','email_receiver')

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
