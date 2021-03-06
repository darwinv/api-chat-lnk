"""Conexiones a Channels."""
from channels import Group
# from channels.security.websockets import allowed_hosts_only
from channels.sessions import channel_session
import json
from linkupapi.settings_secret import URL_HOST
import requests
# from django.urls import reverse


# Connected to websocket.connect
# @allowed_hosts_only
@channel_session
def ws_connect(message):
    """Conexion a WebSocket."""
    message.reply_channel.send({"accept": True})  # Se Acepta la conexion
    # Creamos la sala, (id de usuario - id especialidad)
    sala = message['path'].strip('/').split('/')[0]
    # Lo agregamos a un grupo
    Group('chat-' + sala).add(message.reply_channel)
    # lo agregamos a la sesion de channels
    message.channel_session['room'] = sala


@channel_session
def ws_receive(message):
    """Funcion que recibe data de el socket de cliente."""
    # obj_api = api()
    # sala = message.channel_session['room']

    # room = Room.objects.get(label=label)
    # -- aca se podria enviar el request para la api --
    data = json.loads(message['text'])
    # import pdb; pdb.set_trace()
    # m = room.messages.create(handle=data['handle'], message=data['message'])
    # data["text"] = data['message']
    send_api(token=data['token'], arg=data)


@channel_session
def ws_disconnect(message):
    """Desconectar."""
    if message.channel_session and "room" in message.channel_session:
        label = message.channel_session['room']
        Group('chat-'+label).discard(message.reply_channel)


def send_api(token='', arg=None, files=None):
    """Funcion para llamarse a la api."""
    headers = {'Accept-Language': 'es'}

    url = URL_HOST
    if token:
        headers['Authorization'] = 'Bearer {}'.format(token)
        if arg["message"][0]["msg_type"] == 'q':
            slug = 'client/queries'
            r = requests.post(url + slug + '/', headers=headers, json=arg)
        else:
            slug = 'specialist/queries' + '/' + str(arg["query"])
            r = requests.put(url + slug + '/', headers=headers, json=arg)
        print(r)
