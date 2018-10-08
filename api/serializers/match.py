"""Serializers del Match."""
from rest_framework import serializers
from api.models import Match, MatchFile, MatchProduct, Specialist
from django.utils.translation import ugettext_lazy as _
from api.serializers.actors import ClientSerializer
from api.api_choices_models import ChoicesAPI as ch


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
    
    def validate(self, data):
        """validate Redefinido."""
        msg = _("you can not hire that specialty anymore")
        qs = Match.objects.filter(category=data["category"],
                                  client=data["client"])
        if qs.exists():
            raise serializers.ValidationError({"category": [msg]})

        return data

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


class MatchAcceptSerializer(serializers.ModelSerializer):
    """Aceptar match ."""
    payment_option_specialist = serializers.ChoiceField(
            choices=ch.match_paid_specialist, required=True)

    class Meta:
        """Meta."""
        model = Match
        fields = ('payment_option_specialist', 'status')

    def update(self, instance, validated_data):
        """Redefinir update."""
        instance.payment_option_specialist = validated_data["payment_option_specialist"]
        instance.status = 2
        instance.save()
        return instance


class MatchDeclineSerializer(serializers.ModelSerializer):
    """Aceptar match ."""
    declined_motive = serializers.CharField(max_length=255)

    class Meta:
        """Meta."""
        model = Match
        fields = ('declined_motive', 'status')

    def update(self, instance, validated_data):
        """Redefinir update."""
        instance.declined_motive = validated_data["declined_motive"]
        instance.status = 3
        instance.save()
        return instance


class MatchListClientSerializer(serializers.ModelSerializer):
    """Listado de Matchs."""
    class Meta:
        model = Match
        fields = ('category', 'subject', 'file', 'client')

    def to_representation(self, obj):
        """Redefinido metodo de to_representation."""

        files = ListFileSerializer(obj.matchfile_set.all(), many=True).data

        if obj.status == 5:
            specialist = {"code": obj.specialist.code,
                          "first_name": obj.specialist.first_name,
                          "last_name": obj.specialist.last_name,
                          "email_exact": obj.specialist.email_exact,
                          "telephone": obj.specialist.telephone,
                          "cellphone": obj.specialist.cellphone,
                          "photo": obj.specialist.photo}
        else:
            specialist = None

        return {"id": obj.id, "date": str(obj.created_at),
                "subject": obj.subject, "category": _(obj.category.name),
                "specialist": specialist, "category_image": obj.category.image,
                "file": files, "status": obj.status,
                "declined_motive": obj.declined_motive}



class MatchListSerializer(serializers.ModelSerializer):
    """Listado de Matchs."""
    class Meta:
        model = Match
        fields = ('category', 'subject', 'file', 'client', 'specialist')

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
        client = ClientSerializer(obj.client)

        return {"id": obj.id, "date": str(obj.created_at),
                "subject": obj.subject, "category": _(obj.category.name),
                "specialist": specialist, "category_image": obj.category.image,
                "file": files, "status": obj.status, "client": client.data,
                "payment_option_specialist":obj.payment_option_specialist}

class MatchListSpecialistSerializer(serializers.ModelSerializer):
    """Listado de Matchs."""
    class Meta:
        model = Match
        fields = ('category', 'subject', 'file', 'specialist')

    def to_representation(self, obj):
        """Redefinido metodo de to_representation."""

        files = ListFileSerializer(obj.matchfile_set.all(), many=True).data

        if obj.status == 5:
            client = ClientSerializer(obj.client)
            client_data = client.data
        else:
            client_data = None

        return {"id": obj.id, "date": str(obj.created_at),
                "subject": obj.subject, "category": _(obj.category.name),
                "client": client_data, "category_image": obj.category.image,
                "file": files, "status": obj.status,
                "declined_motive": obj.declined_motive}
