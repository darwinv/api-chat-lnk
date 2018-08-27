"""Estados de cuenta."""
from rest_framework import serializers
from api.models import Specialist, Query
from django.utils.translation import ugettext_lazy as _


class SpecialistAccountSerializer(serializers.ModelSerializer):
    """Serializer de Especialidades."""

    name = serializers.SerializerMethodField()

    class Meta:
        """Modelo Category y sus campos."""

        model = Specialist
        fields = ('id')

    def to_representation(self, obj):
        """To Representation."""
