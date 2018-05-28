from rest_framework.decorators import api_view
from api.emails import BasicEmailAmazon
from rest_framework.response import Response
from channels import Group
from channels.sessions import channel_session
from chat.models import Room
import json
import pyrebase


# @channel_session
# Solo demostracion
@api_view(['POST'])
def chat(request):
    """Solo Demostración."""
    config = { "apiKey": "AIzaSyDXfelS4nVgbWSI8pAR4JMV14QB5WnEL4A",
               "authDomain": "demofirebase-2ae8f.firebaseapp.com",
               "databaseURL": "https://demofirebase-2ae8f.firebaseio.com",
               "projectId": "demofirebase-2ae8f",
               "storageBucket": "demofirebase-2ae8f.appspot.com"}
    firebase = pyrebase.initialize_app(config)

    if request.method == 'POST':
        db = firebase.database()
        data = {"title": request.data["title"], "message": request.data["message"], "type": request.data["type"]}
        db.child("consulta").push(data)
        label = 1  # request.data["room"]  # message.channel_session['room']
        room = Room.objects.get(label=label)
        m = room.messages.create(handle=request.data['title'], message=request.data['message'])
        # data["text"] = data['message']
        # result = obj_api.post(slug='chat/', token='', arg=data)
        # print(result)

        Group('chat-'+str(label)).send({'text': json.dumps(m.as_dict())})
        # Code block for POST request
        # print(request.data)
        return Response("exit")
    # else:
        # Code block for GET request (will also match PUT, HEAD, DELETE, etc)
