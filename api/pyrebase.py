"""Funcionamiento de Pyrebase."""
import pyrebase
from datetime import datetime, timedelta
from api.utils.parameters import Params, Payloads
from linkupapi.settings import CONFIG_ENVIROMENT

config = CONFIG_ENVIROMENT

def chat_firebase_db(data, room):
    """Enviar data a firebase en chat."""
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    if exist_room(db, room):
        res = db.child("chats").child(room).update(data)
    else:
        res = db.child("chats").child(room).set(data)
    return res


def exist_room(db, room):
    """Chequear si el nodo de sala existe."""
    return db.child("chats").child(room).get() is not None


def categories_db(client_id, cat_id):
    # Actualizar la hora de del momento en que se realiza una consulta
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    node_client = Params.PREFIX['client'] + str(client_id)
    node_category = Params.PREFIX['category'] + str(cat_id)
    time_now = str(datetime.now())
    read = False
    data = {
        "datetime": time_now,
        "id": cat_id,
        "read": read
    }
    res = db.child("categories/clients").child(node_client).child(node_category).update(data)
    return res


def createCategoriesLisClients(client_id):
    #funcion para crear la lista completa de categorias al momento de darse de alta un cliente
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    node_client = Params.PREFIX['client'] + str(client_id)
    res = db.child("categories/clients").child(node_client).update(Payloads.categoriesList)
    return res


def createListMessageClients(lista, client_id):
    # funsion para insertar o actualizar los mensajes de los clientes del especialista
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    data_obj = lista[0]
    node_specialist = Params.PREFIX['specialist'] + str(data_obj['specialist'])
    node_client = Params.PREFIX['client'] + str(client_id)
    data_obj['date'] = str(data_obj['date'])

    res = db.child("messagesList/specialist/").child(node_specialist).child(node_client).update(data_obj)
    return res
