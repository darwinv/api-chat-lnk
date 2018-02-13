"""Activacion y modificacion de planes."""
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import permissions
from api.models import Client
from django.http import Http404
from rest_framework.response import Response
from api.serializers.plan import PlanDetailSerializer, ActivePlanSerializer
from api.models import QueryPlansAcquired
from django.db.models import F

class ActivationPlanView(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return QueryPlansAcquired.objects.get(pk=pk)
        except QueryPlansAcquired.DoesNotExist:
            raise Http404

    def get(self, request, code):
        client = request.user.id
        query_set = self.get_detail_plan(code, client)
        try:
            serializer = PlanDetailSerializer(query_set)
            return Response(serializer.data)
        except Exception as e:
            print(e)
            raise Http404

    def put(self, request, code):
        """Activar producto, via codigo PIN."""
        data = request.data
        client = request.user.id
        plan_acquired = self.get_detail_plan(code, client)

        query_set = self.get_object(plan_acquired['id'])

        serializer = ActivePlanSerializer(query_set, data, partial=True)
        # import pdb
        # pdb.set_trace()
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get_detail_plan(self, code, client):
        try:
            # EL SIGUIENTE QUERY DEBE SER OPTIMIZADO Y REUTILIZADO PARA DIFERENTES SERVICIOS
            # Query para traer el detalle de un plan por el codigo PIN
            return QueryPlansAcquired.objects.values('id', 'is_active', 'plan_name',
                                              'query_quantity', 'available_queries',
                                              'validity_months','expiration_date','sale_detail__price')\
            .annotate(price=F('sale_detail__price'))\
            .filter(sale_detail__sale__client= client, sale_detail__pin_code=code, is_active = False)[:1].get()
            
        except QueryPlansAcquired.DoesNotExist:
            raise Http404