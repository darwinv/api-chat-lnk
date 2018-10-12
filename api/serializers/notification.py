"""Notification Serializer."""
from rest_framework import serializers


class NotificationSerializer(serializers.Serializer):
    """Serializer de data pendiente."""
    def to_representation(self, instance):
        return {
                "id": instance.id,
                }
