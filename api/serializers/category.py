from rest_framework import serializers
from api.models import Category
from django.utils.translation import ugettext_lazy as _
class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'description')

    def get_name(self, obj):
        return _(obj.name)
