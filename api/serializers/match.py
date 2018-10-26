"""Serializers del Match."""
from rest_framework import serializers

from api.models import Match, MatchFile, MatchProduct, Specialist, Sale, SaleDetail

from django.utils.translation import ugettext_lazy as _
from api.serializers.actors import ClientSerializer, SpecialistSerializer
from api.api_choices_models import ChoicesAPI as ch
from api.serializers.sale import increment_reference
class ListFileSerializer(serializers.ModelSerializer):
    """Serializer para la representacion del mensaje."""
    class Meta:
        model = MatchFile
        fields = ('id', 'file_url', 'file_preview_url', 'content_type')
        read_only_fields = ('file_preview_url',)


class MatchFileSerializer(serializers.ModelSerializer):
    """Serializer de archivo."""
    class Meta:
        model = MatchFile
        fields = ('file_url', 'content_type')


class MatchDetailSerializer(serializers.ModelSerializer):
    """Match Detalle."""
    file = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ('category', 'subject', 'file', 'client', 'price',
                  'status')

    def get_file(self, obj):
        """Devuelve lista de archivos."""
        files = ListFileSerializer(obj.matchfile_set.all(), many=True).data
        return files

class MatchSerializer(serializers.ModelSerializer):
    """Serializer Match."""
    file = MatchFileSerializer(many=True, required=False)

    class Meta:
        model = Match
        fields = ('category', 'subject', 'file', 'client')

    def validate(self, data):
        """validate Redefinido."""
        msg = _("you can not hire that specialty anymore")
        # no puede contratar un match con la especialidad si aun  no se ha resuelto,
        # o si ya fue exitoso
        qs = Match.objects.filter(category=data["category"],
                                  client=data["client"]).exclude(status=3)
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

        is_client = Sale.objects.filter(
                                        saledetail__is_billable=True,
                                        client=validated_data["client"],
                                        status__range=(2, 3)).exists()
        if is_client:
            is_billable = False
        else:
            is_billable = True

        # Crear compra del match
        sale = Sale.objects.create(place="BCP", total_amount=validated_data["price"],
                                   reference_number=increment_reference(),
                                   description='pago de match',
                                   client=validated_data["client"], status=1)        

        # Detalle de la compra del match
        sale_detail = SaleDetail.objects.create(price=validated_data["price"],
                                                description="Contratacion de especialista",
                                                discount=float(0),
                                                pin_code='XXXXXX',
                                                is_billable=is_billable,
                                                product_type_id=2, sale=sale)
        
        validated_data["sale_detail"] = sale_detail

        data_files = validated_data.pop('file', None)
        match = Match.objects.create(**validated_data)
        if data_files is not None:
            for data_file in data_files:
                MatchFile.objects.create(match=match, **data_file)


        return match

    def to_representation(self, obj):
        """Redefinido metodo de representación del serializer."""
        display_name = ''
        files = ListFileSerializer(obj.matchfile_set.all(), many=True).data
        files_ids = []
        for file_obj in files:
            files_ids.append(file_obj["id"])

        if obj.client.type_client == 'n':
            display_name = obj.client.first_name + ' ' + obj.client.last_name
        else:
            display_name = obj.client.agent_firstname + ' ' + obj.client.agent_lastname

        if obj.client.nick is not None:
            if len(obj.client.nick) > 0:
                display_name = obj.client.nick

        return {"id": obj.id, "file": files,
                "category": obj.category.id,
                "subject": obj.subject, "client": obj.client.id,
                "specialist": obj.specialist.id,
                "display_name": display_name,
                "photo": obj.client.photo,
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

    def to_representation(self, obj):
        """to Representacion."""
        # cuando se declina el nombre a devolver es el especialista
        # ya que se le envia al cliente en el notification push
        display_name = obj.specialist.first_name + ' ' + obj.specialist.last_name

        if obj.specialist.nick is not None:
            if len(obj.specialist.nick) > 0:
                display_name = obj.specialist.nick

        return {"id": obj.id, "category": obj.category.id,
                "subject": obj.subject, "client": obj.client.id,
                "specialist": obj.specialist.id,
                "display_name": display_name,
                "photo": obj.category.image,
                "declined_motive": obj.declined_motive}


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
        if obj.sale_detail:
            sale = obj.sale_detail.sale.id
        else:
            sale = None

        return {"id": obj.id, "date": str(obj.created_at),
                "subject": obj.subject, "category": _(obj.category.name),
                "specialist": specialist, "category_image": obj.category.image,
                "file": files, "status": obj.status,
                "declined_motive": obj.declined_motive,
                "sale":sale, "price":obj.price}



class MatchListSerializer(serializers.ModelSerializer):
    """Listado de Matchs."""
    class Meta:
        model = Match
        fields = ('category', 'subject', 'file', 'client', 'specialist')

    def to_representation(self, obj):
        """Redefinido metodo de to_representation."""
        files = ListFileSerializer(obj.matchfile_set.all(), many=True).data

        specialist = SpecialistSerializer(obj.specialist)
        client = ClientSerializer(obj.client)

        return {"id": obj.id, "date": str(obj.created_at),
                "subject": obj.subject, "category": _(obj.category.name),
                "specialist": specialist.data, "category_image": obj.category.image,
                "file": files, "status": obj.status, "client": client.data,
                "payment_option_specialist":obj.payment_option_specialist,
                "price": obj.price}

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
                "declined_motive": obj.declined_motive, "price":obj.price}
