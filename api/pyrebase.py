"""Funcionamiento de Pyrebase."""
import pyrebase
from api.models import Client, QueryPlansAcquired
# from datetime import datetime, timedelta
from api.utils.parameters import Params, Payloads
from api.utils.querysets import get_query_set_plan
from api.serializers.plan import QueryPlansAcquiredSerializer
from linkupapi.settings import CONFIG_ENVIROMENT
config = CONFIG_ENVIROMENT
# Sugerencia para cambiar por una clase con sus metodos


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


def categories_db(client_id, cat_id, time_now, read=False):
    """Acualizar Listado de Categorias del Chat."""
    # Actualizar la hora de del momento en que se realiza una consulta
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    node_client = Params.PREFIX['client'] + str(client_id)
    node_category = Params.PREFIX['category'] + str(cat_id)

    data = {
        "datetime": time_now,
        "id": cat_id,
        "read": read
    }
    res = db.child("categories/clients").child(
                                 node_client).child(node_category).update(data)
    return res

###########FUNCIONES PARA CREAR NODOS EN FIREBASE MANUALMENTE##########
def update_categories():
    """Cargar listado de categorias para todos los usuarios."""
    # SOLO USO PARA AMBIENTE EN DESARROLLO
    for client in Client.objects.all():
        createCategoriesLisClients(client.id)

def update_plan_choisen():
    """Cargar plan activo para todos los usuarios."""
    # SOLO USO PARA AMBIENTE EN DESARROLLO
    for client in Client.objects.all():
        try:
            print("new")
            plan_chosen = get_query_set_plan()
            plan_active = plan_chosen.filter(client= client.id, is_active = True, is_chosen = True)[:1].get()

            obj = QueryPlansAcquired.objects.get(pk=plan_active['id'])
            plan = QueryPlansAcquiredSerializer(obj)
            chosen_plan(Params.PREFIX['client'] + str(client.id), plan.data)

        except Exception as e:
            pass

########### FIN DE FUNCIONES PARA CREAR NODOS EN FIREBASE MANUALMENTE#####


def createCategoriesLisClients(client_id):
    """Crear la lista completa de categorias.

    Al momento de darse de alta un cliente
    """
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    node_client = Params.PREFIX['client'] + str(client_id)
    res = db.child("categories/clients").child(
        node_client).update(Payloads.categoriesList)
    return res


def createListMessageClients(lista, client_id):
    """Insertar o actualizar los mensajes de los clientes del especialista."""
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    data_obj = lista[0]
    node_specialist = Params.PREFIX['specialist'] + str(data_obj['specialist'])
    node_client = Params.PREFIX['client'] + str(client_id)
    data_obj['date'] = str(data_obj['date'])
    res = db.child("messagesList/specialist/").child(
        node_specialist).child(node_client).update(data_obj)
    return res


def chosen_plan(client_id, data):
    """Actualizar el plan elegido por cliente."""
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    res = db.child("chosenPlans").child(client_id).update(data)
    return res


def mark_uploaded_file(room, message_id):
    """Actualizar que el archivo se ha subido a firebase."""
    node = 'chats/room/' + 'm' + str(message_id)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    db.child(node).update({"uploaded": 1})
