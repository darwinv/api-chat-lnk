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
    class Meta:
        model = Query
        fields = ('title', 'message', 'status', 'category', 'client', 'specialist')
