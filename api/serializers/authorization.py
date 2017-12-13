from rest_framework import serializers
from api.models import Client, User
class ClientAuthorization(serializers.ModelSerializer):
    """Serializer del especialista."""

    code_seller = serializers.CharField()
    name = serializers.CharField()
    document = serializers.CharField()
    document_type = serializers.CharField()
    document_type_name = serializers.SerializerMethodField()
    status = serializers.CharField()

    class Meta:
        """Modelo del especialista y sus campos."""
        model = User
        fields = ('code_seller','name','document','document_type','status')


    def get_document_type_name(self, obj):
        """Devuelve Ocupación."""
        return _(obj.get_document_type_display())