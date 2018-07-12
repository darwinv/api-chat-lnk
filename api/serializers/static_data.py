"""Especialidades."""
from rest_framework import serializers
from api.models import Objection
from django.utils.translation import ugettext_lazy as _


class ObjectionsSerializer(serializers.ModelSerializer):
    """Serializer de Especialidades."""

    name = serializers.SerializerMethodField()

    class Meta:
        """Modelo Category y sus campos."""

        model = Objection
        fields = ('id', 'name',)

    def get_name(self, obj):
        """Devuelve el nombre de la objecion."""
        return _(obj.name)
