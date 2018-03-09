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
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    node_client = Params.PREFIX['client'] + str(client_id)
    time_now = str(datetime.now())
    data = {
        "datetime" : time_now,
        "id" : cat_id
      }
    res = db.child("categories/clients").child(node_client).child(cat_id).update(data)
    return res

def createCategoriesLisClients(client_id):
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    node_client = Params.PREFIX['client'] + str(client_id)
    res = db.child("categories/clients").child(node_client).update(Payloads.categoriesList)
    return res