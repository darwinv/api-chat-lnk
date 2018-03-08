"""Vista de sala de chats."""
from chat.models import Room
from chat.serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
# Create your views here.


@api_view()
def hello_world(request):
    return Response({"message": "Hello, world!"})


@api_view()
def chat_room(request, label):
    """Vista Sala de chat."""
    # If the room with the given label doesn't exist, automatically create it
    # upon first visit (a la etherpad).
    room, created = Room.objects.get_or_create(label=label)

    # We want to show the last 50 messages, ordered most-recent-last
    messages = reversed(room.messages.order_by('-timestamp')[:50])

    serializer = MessageSerializer(messages, many=True)
    # import pdb; pdb.set_trace()
    return Response(serializer.data)

    # return render(request, "chat/room.html", {
    #     'room': room,
    #     'messages': messages,
    # })
