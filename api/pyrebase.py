"""Funcionamiento de Pyrebase."""
import pyrebase
from api.models import Client, QueryPlansAcquired, Category, Message
# from datetime import datetime, timedelta
from api.utils.parameters import Params, Payloads
from api.utils.querysets import get_query_set_plan
from api.serializers.plan import QueryPlansAcquiredSerializer
from linkupapi.settings import CONFIG_ENVIROMENT
config = CONFIG_ENVIROMENT

firebase = pyrebase.initialize_app(config)
db = firebase.database()


# FUNCIONES PARA CREAR NODOS EN FIREBASE MANUALMENTE #
def update_categories_detail():
    """Cargar listado de categorias para todos los usuarios."""
    # SOLO USO PARA AMBIENTE EN DESARROLLO
    for categorie in Category.objects.all():

        firebase = pyrebase.initialize_app(config)
        db = firebase.database()
        node_client = Params.PREFIX['category'] + str(categorie.id)
        res = db.child("categories/categoryDetail").child(
            node_client).update({"description": categorie.description})


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
            plan_active = plan_chosen.filter(client=client.id, is_active=True,
                                             is_chosen=True)[:1].get()

            obj = QueryPlansAcquired.objects.get(pk=plan_active['id'])
            plan = QueryPlansAcquiredSerializer(obj)
            chosen_plan(Params.PREFIX['client'] + str(client.id), plan.data)

        except Exception as e:
            print("error")

# FIN DE FUNCIONES PARA CREAR NODOS EN FIREBASE MANUALMENTE#####


def chat_firebase_db(data, room):
    """Enviar data a firebase en chat."""
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    room = "chats/{}/".format(room)
    if exist_room(room):
        res = db.child(room).update(data)
    else:
        res = db.child(room).set(data)
    return res

def exist_room(room):
    """Chequear si el nodo de sala existe."""
    return db.child(room).get() is not None


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


def updateStatusQueryAccept(specialist_id, client_id, query_id):
    """ Actualizacion query en listado y chat """
    data = {"status": 2}  # Query Aceptado por especialista

    # Remover query del listado de pendientes
    removeQueryAcceptList(specialist_id, client_id, query_id, data)

    # Actualizar estatus de query actual
    update_status_query_current_list(specialist_id, client_id, data, query_id)

    # Actualizar estatus de los mensajes del chat
    data_msgs = Message.objects.filter(query=query_id)
    updateStatusQueryAcceptChat(data_msgs, data)


def removeQueryAcceptList(specialist_id, client_id, query_id, data):
    """ Remover query nodo en listado de clientes """
    node_specialist = Params.PREFIX['specialist'] + str(specialist_id)
    node_client = Params.PREFIX['client'] + str(client_id)
    node_query = 'queries/{}'.format(Params.PREFIX['query'] + str(query_id))

    res = db.child("messagesList/specialist/").child(
        node_specialist).child(node_client).child(node_query).remove()

    return res


def update_status_query_current_list(specialist_id, client_id,
                                     data, query_id=None):

    """ Actualizacion query en listado de clientes"""
    node_specialist = Params.PREFIX['specialist'] + str(specialist_id)
    node_client = Params.PREFIX['client'] + str(client_id)
    node_query = 'queryCurrent'
    room = "messagesList/specialist/{}/{}/{}/".format(node_specialist,
                                                      node_client, node_query)

    node = db.child(room + '/id').get()
    if query_id:
        if node.pyres and node.pyres == query_id:
            res = db.child(room).update(data)
        else:
            pass
            res = None
    else:
        res = db.child(room).update(data)
    return res

def updateStatusQueryAcceptChat(data_msgs, data):
    """ Actualizacion query en el chat """

    for msgs in data_msgs:
        print(db.child("chats").child(msgs.room)\
            .child(Params.PREFIX['message']+str(msgs.id))\
            .child("query")\
            .update(data))

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


def update_status_messages(data_msgs):
    """Actualizar el status si puede o no reconsultar, responder, etc."""
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    for msgs in data_msgs:
        res = db.child("chats").child(msgs.room)\
            .child(Params.PREFIX['message']+str(msgs.id))\
            .update({"groupStatus": 2})
        print(res)


def createListMessageClients(lista, act_query, status,
                             client_id, queries_list=None):
    """Insertar o actualizar los mensajes de los clientes del especialista."""
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    # import pdb; pdb.set_trace()
    data_obj = lista[0]
    node_specialist = Params.PREFIX['specialist'] + str(data_obj['specialist'])
    node_client = Params.PREFIX['client'] + str(client_id)
    data_obj['date'] = str(data_obj['date'])
    data_obj['queries'] = queries_list
    if status >= 4:
        data_obj['isQueryActive'] = False
    else:
        data_obj['isQueryActive'] = True
    query_current = {
        "id": act_query,
        "date": str(data_obj['date']),
        "message": data_obj['message'],
        "title": data_obj['title'],
        "status": status
    }
    data_obj['queryCurrent'] = query_current
    del data_obj['message']
    del data_obj['title']
    res = db.child("messagesList/specialist/").child(
        node_specialist).child(node_client).update(data_obj)
    return res


def chosen_plan(client_id, data):
    """Actualizar el plan elegido por cliente."""
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    res = db.child("chosenPlans").child(client_id).update(data)
    return res


def mark_failed_file(room, message_id):
    """Actualizar que el archivo se ha subido a firebase."""
    node = 'chats/' + room + '/' + 'm' + str(message_id)
    firebase = pyrebase.initialize_app(config)
    # print(node)
    db = firebase.database()
    r = db.child(node).update({"uploaded": 5, "fileUrl": "error"})
    return r


def mark_uploaded_file(room, message_id, url_file):
    """Actualizar que el archivo se ha subido a firebase."""
    node = 'chats/' + room + '/' + 'm' + str(message_id)
    firebase = pyrebase.initialize_app(config)
    # print(node)
    db = firebase.database()
    r = db.child(node).update({"uploaded": 2, "fileUrl": url_file})
    return r
