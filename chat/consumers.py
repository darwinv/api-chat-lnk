from channels import Group
from channels.sessions import channel_session
from .models import Room
import json


@channel_session
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    # import pdb; pdb.set_trace()
    print(message['path'])
    prefix, nothing, label = message['path'].strip('/').split('/')
    room = Room.objects.get(label=label)
    Group('chat-' + label).add(message.reply_channel)
    message.channel_session['room'] = room.label


@channel_session
def ws_receive(message):
    # obj_api = api()
    label = message.channel_session['room']
    room = Room.objects.get(label=label)
    data = json.loads(message['text'])
    m = room.messages.create(handle=data['handle'], message=data['message'])
    data["text"] = data['message']
    # result = obj_api.post(slug='chat/', token='', arg=data)
    # print(result)
    Group('chat-'+label).send({'text': json.dumps(m.as_dict())})


@channel_session
def ws_disconnect(message):
    label = message.channel_session['room']
    Group('chat-'+label).discard(message.reply_channel)
