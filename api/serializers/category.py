"""Especialidades."""
from rest_framework import serializers
from api.models import Category
from django.utils.translation import ugettext_lazy as _


class CategorySerializer(serializers.ModelSerializer):
    """Serializer de Especialidades."""

    name = serializers.SerializerMethodField()

    class Meta:
        """Modelo Category y sus campos."""

        model = Category
        fields = ('id', 'name', 'image', 'description')

    def get_name(self, obj):
        """Devuelve el nombre de la especialidad."""
        return _(obj.name)
