"""Funcionamiento de Pyrebase."""
import pyrebase
config = {
    "apiKey": "AIzaSyAkGuOIe3oZhW2PKh6sn2qNwa1QM91JgNQ",
    "authDomain": "linkup-peru.firebaseapp.com",
    "databaseURL": "https://linkup-peru.firebaseio.com",
    "projectId": "linkup-peru",
    "storageBucket": "linkup-peru.appspot.com"
}


# class
def chat_firebase_db(data, room):
    """Enviar data a firebase en chat."""
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    res = db.child("chatNew").child(room).set(data)
    return res
