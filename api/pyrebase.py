"""Funcionamiento de Pyrebase."""
import pyrebase
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
    res = db.child("chats").child(room).set(data)
    return res
