"""Conexiones a Channels."""
from channels import Group
from channels.sessions import channel_session
from .models import Room
import json
import requests
# from django.urls import reverse


@channel_session
def ws_connect(message):
    """Conexion a WebSocket."""
    message.reply_channel.send({"accept": True})  # Se Acepta la conexion
    # import pdb; pdb.set_trace()
    prefix, label = message['path'].strip('/').split('/')
    room = Room.objects.get(label=label)
    Group('chat-' + label).add(message.reply_channel)
    message.channel_session['room'] = room.label


@channel_session
def ws_receive(message):
    """Funcion que recibe data de el socket de cliente."""
    # obj_api = api()
    label = message.channel_session['room']

    # room = Room.objects.get(label=label)
    # -- aca se podria enviar el request para la api --
    data = json.loads(message['text'])
    payload = {
        "title": data['handle'],
        "category": data['category'],
        "message": [{
            "message": data['message'],
            "msg_type": "q",
            "content_type": "0",
            "file_url": ""
            }]
    }
    # m = room.messages.create(handle=data['handle'], message=data['message'])
    # data["text"] = data['message']
    send_api(token=data['token'], arg=payload)


@channel_session
def ws_disconnect(message):
    """Desconectar."""
    label = message.channel_session['room']
    Group('chat-'+label).discard(message.reply_channel)


def send_api(token='', arg=None, files=None):
    """Funcion para llamarse a la api."""
    headers = {'Accept-Language': 'es'}
    url = 'http://127.0.0.1:8000/'
    slug = 'client/queries'
    if token:
        headers['Authorization'] = 'Bearer {}'.format(token)
        headers = dict(headers, **{'x-api-key': '90bd028513c2440f9c262c5c09c668e5'})
        r = requests.post(url + slug + '/', headers=headers, json=arg, files=files)
        print(r.json())