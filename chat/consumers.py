from channels import Group
from channels.sessions import channel_session
from .models import Room
import json
import requests
from django.urls import reverse

@channel_session
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    # import pdb; pdb.set_trace()
    print(message['path'])
    prefix, label = message['path'].strip('/').split('/')
    room = Room.objects.get(label=label)
    Group('chat-' + label).add(message.reply_channel)
    message.channel_session['room'] = room.label


@channel_session
def ws_receive(message):
    """Funcion que recibe data de el socket de cliente."""
    # obj_api = api()
    label = message.channel_session['room']
    room = Room.objects.get(label=label)
    # -- aca se podria enviar el request para la api --
    data = json.loads(message['text'])
    # mensaje = {
    #     "message": "Lorem ipsum dolor sit amet,anctus e",
    #     "msg_type": "q",
    #     "media_files": []
    # }
    payload = {
        "title": data['handle'],
        "category": 1,
        "message": {
            "message": data['message'],
            "msg_type": "q",
            "media_files": []
        }
    }
    m = room.messages.create(handle=data['handle'], message=data['message'])
    # data["text"] = data['message']
    send_api(token='HhaMCycvJ5SCLXSpEo7KerIXcNgBSt', arg=payload)

    # result = obj_api.post(slug='chat/', token='', arg=data)
    # print(result)
    # Group('chat-'+label).send({'text': json.dumps(m.as_dict())})


@channel_session
def ws_disconnect(message):
    label = message.channel_session['room']
    Group('chat-'+label).discard(message.reply_channel)


def send_api(token='', arg=None, files=None):
    headers = {'Accept-Language': 'es'}
    url = 'http://127.0.0.1:8000/'
    slug = 'client-queries'
    if token:
        headers['Authorization'] = 'Bearer {}'.format(token)
        headers = dict(headers, **{'x-api-key': '90bd028513c2440f9c262c5c09c668e5'})
        r = requests.post(url + slug + '/', headers=headers, json=arg, files=files)
        print(r.json())
