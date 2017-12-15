from rest_framework import serializers
from api.models import Client, User
from api.api_choices_models import ChoicesAPI as c
from django.utils.translation import ugettext_lazy as _

class ClientAuthorization(serializers.ModelSerializer):
    """Serializer del especialista."""

    code_seller = serializers.CharField()
    name = serializers.CharField()
    document = serializers.CharField()
    document_type = serializers.CharField()
    document_type_name = serializers.SerializerMethodField()
    status = serializers.CharField()
    date_join = serializers.CharField()

    class Meta:
        """Modelo del especialista y sus campos."""
        model = User
        fields = ('code_seller', 'name', 'document', 'document_type', 'status', 'document_type_name', 'date_join')

    def get_document_type_name(self, obj):
        """Devuelve Ocupación."""
        return _(obj.get_document_type_display())


class UserStatusSerializer(serializers.ModelSerializer):
    """Serializer para cambiar el status de los usuarios."""

    status = serializers.ChoiceField(choices=c.user_status)

    class Meta:
        """Meta de Modelos."""

        model = User
        fields = ('id', 'status')
