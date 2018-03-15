"""Funcionamiento de Pyrebase."""
import pyrebase
from datetime import datetime
from api.utils.parameters import Params, Payloads

# config = {
#     "apiKey": "AIzaSyAkGuOIe3oZhW2PKh6sn2qNwa1QM91JgNQ",
#     "authDomain": "linkup-peru.firebaseapp.com",
#     "databaseURL": "https://linkup-peru.firebaseio.com",
#     "projectId": "linkup-peru",
#     "storageBucket": "linkup-peru.appspot.com"
# }

config = {
    "apiKey": "AIzaSyDoYMhNo1RP1JYrQN1pX84w4YL82N7MURM",
    "authDomain": "linkup-5b6f4.firebaseapp.com",
    "databaseURL": "https://linkup-5b6f4.firebaseio.com",
    "projectId": "linkup-5b6f4",
    "storageBucket": "linkup-5b6f4.appspot.com"
}


# class
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
    #actualizar la hora de del momento en que se realiza una consulta
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
    #funsion para insertar o actualizar los mensajes de los clientes del especialista
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    data_obj = lista[0]
    node_specialist = Params.PREFIX['specialist'] + str(data_obj['specialist'])
    data_obj['date'] = str(data_obj['date'])
    del (data_obj['specialist'])
    payload = {}
    position = -1
    cont = 0
    #traigo en nodo de mensajes correspondientes al especialista del cliente que ha realizado la consulta
    data = db.child("messageslist/specialist").child(node_specialist).get()
    if data.val() is not None:
        #saco los campos nulos(None), si es que las hay
        list_msgs = [row for row in data.val() if row is not None]
        for i in list_msgs:
            if i['client'] == client_id:
                #obtengo la psision del cliente a actualizar en la lista
                position = cont
            cont += 1
        if position > -1:
            # list_msgs[position] = t
            list_msgs[position] = lista[0]
        else:
            # list_msgs.append(t)
            list_msgs.append(lista[0])
        payload[node_specialist] = list_msgs
    else:
        payload[node_specialist] = lista
    res = db.child("messageslist/specialist/").update(payload)
    return res
