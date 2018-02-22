from rest_framework import serializers
from rest_framework.response import Response
from chat.models import Room, Message


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('room', 'handle', 'message', 'timestamp')



class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ('label', 'name')
