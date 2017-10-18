from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from api.models import User, Client, LevelInstruction, Profession, Role, Countries
from api.models import CommercialGroup, EconomicSector, Address, Department
from api.models import Province, District, Category, Specialist, Query, Answer
from api.models import Parameter
from django.utils import six
import pdb
from datetime import datetime
from django.utils import timezone

class QuerySerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Query.option_status, read_only=True)
    last_time = serializers.SerializerMethodField()
    class Meta:
        model = Query
        fields = ('title', 'message', 'status', 'last_time','category', 'client', 'specialist')

    # Devuelvo la hora y minuto separados
    def get_last_time(self,obj):
        return str(obj.last_modified.date()) + ' ' + str(obj.last_modified.hour) + ':' + str(obj.last_modified.minute)
