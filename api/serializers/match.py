"""Serializers del Match."""
from rest_framework import serializers
from api.models import Match, MatchFile, MatchProduct, Specialist
from django.utils.translation import ugettext_lazy as _

class ListFileSerializer(serializers.ModelSerializer):
    """Serializer para la representacion del mensaje."""
    class Meta:
        model = MatchFile
        fields = ('id', 'file_url', 'content_type')


class MatchFileSerializer(serializers.ModelSerializer):
    """Serializer de archivo."""
    class Meta:
        model = MatchFile
        fields = ('file_url', 'content_type')


class MatchSerializer(serializers.ModelSerializer):
    """Serializer Match."""
    file = MatchFileSerializer(many=True)

    class Meta:
        model = Match
        fields = ('category', 'subject', 'file', 'client')

    def create(self, validated_data):
        """Redefinido Crear Serializer."""
        validated_data["specialist"] = Specialist.objects.get(
            type_specialist="m",
            category_id=validated_data["category"])
        # import pdb; pdb.set_trace()
        validated_data["price"] = MatchProduct.objects.first().price
        validated_data["status"] = 1
        data_files = validated_data.pop('file')
        match = Match.objects.create(**validated_data)
        for data_file in data_files:
            MatchFile.objects.create(match=match, **data_file)

        return match

    def to_representation(self, obj):
        """Redefinido metodo de representación del serializer."""
        files = ListFileSerializer(obj.matchfile_set.all(), many=True).data
        files_ids = []
        for file_obj in files:
            files_ids.append(file_obj["id"])

        return {"id": obj.id, "file": files,
                "category": obj.category.id,
                "subject": obj.subject, "client": obj.client.id,
                "specialist": obj.specialist.id,
                "files_id": files_ids}


class MatchListClientSerializer(serializers.ModelSerializer):
    """Listado de Matchs."""
    class Meta:
        model = Match
        fields = ('category', 'subject', 'file', 'client')

    def to_representation(self, obj):
        """Redefinido metodo de to_representation."""

        files = ListFileSerializer(obj.matchfile_set.all(), many=True).data
        specialist = {"code": obj.specialist.code,
                      "first_name": obj.specialist.first_name,
                      "last_name": obj.specialist.last_name,
                      "email_exact": obj.specialist.email_exact,
                      "telephone": obj.specialist.telephone,
                      "cellphone": obj.specialist.cellphone,
                      "photo": obj.specialist.photo}
        # comparo el estado actual del match para devolver un estado especifico
        # para el cliente
        # 1 = esperando respuesta, 2 = pendiente de pago del cliente
        # 3 = Aceptado, 4 = declinado
        if obj.status <= 2:
            status_client = 1
        elif obj.status == 3:
            status_client = 4
        elif obj.status == 4:
            status_client = 2
        elif obj.status == 5:
            status_client = 3

        return {"id": obj.id, "date": str(obj.created_at),
                "subject": obj.subject, "category": _(obj.category.name),
                "specialist": specialist, "category_image": obj.category.image,
                "file": files, "status_client": status_client}
