from django.db import models
from django.utils import timezone
# Create your models here.
# Ejemplo para el chat
class Room(models.Model): 
    """Sala."""

    name = models.TextField()
    label = models.SlugField(unique=True)


class Message(models.Model):
    """Mensajes."""

    room = models.ForeignKey(Room, related_name='messages')
    handle = models.TextField()
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%H:%M:%S')

    def as_dict(self):
        return {'handle': self.handle, 'message': self.message, 'timestamp': self.formatted_timestamp}