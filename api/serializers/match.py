"""Serializers del Match."""
from rest_framework import serializers
from api.models import Match, MatchFile, MatchProduct, Specialist


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
