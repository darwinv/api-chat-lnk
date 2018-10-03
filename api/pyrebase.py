"""Funcionamiento de Pyrebase."""
import pyrebase

from api.models import Client, QueryPlansAcquired, Category, Message, Query
from api.models import SpecialistMessageList_sp, Specialist
from api.serializers.actors import SpecialistMessageListCustomSerializer
from api.serializers.actors import PendingQueriesSerializer
from django.db.models import OuterRef, Subquery, Count

# from datetime import datetime, timedelta
from api.utils.parameters import Params, Payloads
from api.utils.querysets import get_query_set_plan
from api.serializers.plan import QueryPlansAcquiredSerializer
from linkupapi.settings import CONFIG_ENVIROMENT
from linkupapi.settings import DEBUG_FIREBASE
from api.logger import manager
logger = manager.setup_log(__name__)

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
            plan_chosen = get_query_set_plan()
            plan_active = plan_chosen.filter(queryplansclient__client=client.id, is_active=True,
                                             queryplansclient__is_chosen=True)
            if plan_active:
                plan = QueryPlansAcquiredSerializer(plan_active[0])
                chosen_plan(client.id, plan.data)
                print("success")
            print("empty")
        except Exception as e:
            print("error"+str(e))

def update_specialist_client():
    """Cargar listado de categorias para todos los usuarios."""
    # SOLO USO PARA AMBIENTE EN DESARROLLO
    # ESTA FUNCION NO ESTA OPTIMIZADA O SEGURA
    for specialist in Specialist.objects.all():

        for query in Query.objects.filter(specialist=specialist):
            # Generar nodos de listado para nuevo especialista
            generateDataMessageClients(query.client.id, query.category.id, query.id,
                                   query.status, specialist.id)


def delete_node_categories_client():
    """Eliminar nodo de categorias de cliente"""

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    db.child("categories/clients").remove()
# FIN DE FUNCIONES PARA CREAR NODOS EN FIREBASE MANUALMENTE#####


def check_type_data(type_data, node):
    """Chequear tipos de datos en los nodos """
    pass

    # data_chat_string = [
    #     'codeUser', 'fileUrl', 'filePreviewUrl',
    #     'message', 'messageType', 'room',
    #     ]
    #
    # data_chat_int = [
    #     'fileType', 'groupId', 'groupStatus', 'id',
    #     'messageReference', 'uploaded', 'user_id']
    #
    # # data_msgs_string = ['displayName', 'photo', ]
    # nodo = db.child(node).get()
    # ns = list(nodo.val().values())
    # if type_data == 'chats':
    #     size = len(node.split('/'))
    #     if size == 2:
    #         new_str = ns[0]['query'].keys()
    #     elif size == 3:
    #         new_str = nodo.val().get('query').keys()
    #
    #     data_chat_int.extend(new_str)
    #     if 'title' in data_chat_int:
    #         data_chat_int.remove('title')
    #     for n in nodo.val().values():
    #         for l in data_chat_string:
    #             if n['query'].get(l):
    #                 if type(n['query'].get(l)) is not str:
    #                         logger.error("{} - query/{} no es String".format(node, l))
    #             if type(n.get(l)) is not str:
    #                 logger.error("{} - {} no es String".format(node, l))
    #         for k in data_chat_int:
    #             if n['query'].get(k):
    #                 if type(n['query'].get(k)) is not int:
    #                         logger.error("{} - query/{} no es int".format(node, k))
    #             else:
    #                 if type(n.get(k)) is not int:
    #                     logger.error("{} - {} no es int".format(node, k))
    # logger.info('chequeo de data realizada')


def chat_firebase_db(data, room):
    """Enviar data a firebase en chat."""
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    room = "chats/{}".format(room)
    if exist_node(room):
        res = db.child(room).update(data)
    else:
        res = db.child(room).set(data)
    # chequear que los tipos de datos correspondan
    if DEBUG_FIREBASE:
        check_type_data('chats', room)
    return res


def node_query(data, id, room):
    """Actualizar o crear nodos de consulta."""
    node = "queries/{}/{}".format(room, Params.PREFIX['query'] + str(id))
    if exist_node(node):
        res = db.child(node).update(data)
    else:
        print("creo")
        res = db.child(node).set(data)
    if res:
        if "succes" in res:
            if res["success"] != 1:
                logger.error("actualizando node query fallo ".format(node))
    # pass


def exist_node(node):
    """Chequear si el nodo de sala existe."""
    res = db.child(node).get()
    print(node)
    print(res)
    if res.pyres:
        return True
    else:
        return False


def categories_db(client_id, cat_id, time_now=None, read=False):
    """Acualizar Listado de Categorias del Chat."""
    # Actualizar la hora de del momento en que se realiza una consulta
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    node_client = Params.PREFIX['client'] + str(client_id)
    node_category = Params.PREFIX['category'] + str(cat_id)
    main_node = 'categories/clients/' + node_client + '/' + node_category
    pending = Message.objects.filter(query__status=3,
                                     viewed=0, msg_type='a',
                                     query__category=cat_id,
                                     query__client=client_id).count()
    data = {
        # "datetime": time_now,
        "id": int(cat_id),
        "read": read,
        "pendingRead": pending
    }
    if time_now:
        data["datetime"] = time_now
    # print(data["id"])
    if exist_node(main_node):
        res = db.child("categories/clients").child(
            node_client).child(node_category).update(data)
    else:
        res = db.child("categories/clients").child(
            node_client).child(node_category).set(data)
        logger.warning("no existia nodo:" + main_node)
    return res


def updateStatusQueryAccept(specialist_id, client_id, query_id, room=None):
    """ Actualizacion query en listado y chat """
    data = {"status": 2}  # Query Aceptado por especialista

    # Remover query del listado de pendientes
    removeQueryAcceptList(specialist_id, client_id, query_id)

    # Actualizar estatus de query actual
    update_status_query_current_list(specialist_id, client_id, data, query_id)

    # Actualizar estatus de los consulta en el nodo de query
    # data_msgs = Message.objects.filter(query=query_id)
    update_status_query(query_id, data, room)


def updateStatusQueryDerive(old_specialist_id, specialist_id, query):
    """
        old_specialist_id: anterior especialista
        specialist_id: nuevo especialista
        query: instancia del query a modificar
    """
    """ Actualizacion query en listado y chat """
    status = 1
    data = {"status": status, 'specialist_id': int(specialist_id)}  # Query Aceptado por especialista

    client_id = query.client.id
    query_id = query.id
    category_id = query.category.id
    room = query.message_set.last().room

    # Remover query del listado de especialista actual
    removeQueryAcceptList(old_specialist_id, client_id, query_id)

    # Actualizar estatus de query actual especialista anterior
    update_status_query_current_list(old_specialist_id, client_id,
                                     data, query_id)

    # Generar nodos de listado para nuevo especialista
    generateDataMessageClients(client_id, category_id, query_id,
                               status, specialist_id)

    # Actualizar estatus de las consultas
    update_status_query(query_id, data, room)


def removeQueryAcceptList(specialist_id, client_id, query_id):
    """ Remover query nodo en listado de clientes """
    node_specialist = Params.PREFIX['specialist'] + str(specialist_id)
    node_client = Params.PREFIX['client'] + str(client_id)
    node_query = 'queries/{}'.format(Params.PREFIX['query'] + str(query_id))

    main_node = "messagesList/specialist/{}/{}/{}".format(node_specialist,
                                                          node_client,
                                                          node_query)
    if exist_node(main_node):
        db.child("messagesList/specialist/").child(
            node_specialist).child(node_client).child(node_query).remove()
    else:
        logger.warning(
            "RemoveQueryAccept: no existe nodo {}".format(main_node))


def update_status_query_current_list(specialist_id, client_id,
                                     data, query_id=None):
    """ Actualizacion query en listado de clientes."""
    node_specialist = Params.PREFIX['specialist'] + str(specialist_id)
    node_client = Params.PREFIX['client'] + str(client_id)
    node_query = 'queryCurrent'

    room = "messagesList/specialist/{}/{}/{}/".format(node_specialist,
                                                      node_client, node_query)
    if query_id:
        node = db.child(room + 'id').get()
        if node.pyres and node.pyres == int(query_id):
            res = db.child(room).update(data)
        else:
            logger.warning(
                'status_query_currentlist-queryid nodo no existe {}'.format(room))
            res = None
    else:
        if exist_node(room):
            res = db.child(room).update(data)
        else:
            logger.warning(
                'status_query_currentlist nodo no existe {}'.format(room))
    return res


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


def update_status_query(query_id, data, room):
    """Actualizar query de los mensajes."""
    node_query(data=data, id=query_id, room=room)
    # check_type_data('chats', 'chats/{}'.format(data_msgs[0].room))


def update_status_group_messages(data_msgs, status):
    """Actualizar el status si puede o no reconsultar, responder, etc."""
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    for msgs in data_msgs:
        node_msg = Params.PREFIX['message']+str(msgs.id)
        node = 'chats/{}/{}/'.format(msgs.room, node_msg)
        if exist_node(node):
            db.child(node).update({"groupStatus": status})
        else:
            logger.warning(
                'update_statusgroup nodo no existe - chats/{}/{}'
                .format(msgs.room, node_msg))


def set_message_viewed(data_msgs):
    """Actualizar el status de visto para los mensajes."""
    for msgs in data_msgs:
        node_msg = Params.PREFIX['message']+str(msgs.id)
        node = 'chats/{}/{}/'.format(msgs.room, node_msg)

        if exist_node(node):
            db.child(node).update({"read": True})
        else:
            logger.warning(
                'set_message_viewed nodo no existe - chats/{}/{}'
                .format(msgs.room, node_msg))


def createListMessageClients(lista, query_id, status,
                             client_id, specialist_id, queries_list=None):
    """Insertar o actualizar los mensajes de los clientes del especialista."""
    data_obj = lista[0]

    node_specialist = Params.PREFIX['specialist'] + str(specialist_id)
    node_client = Params.PREFIX['client'] + str(client_id)

    if status >= 4:
        data_obj['isQueryActive'] = False
    else:
        data_obj['isQueryActive'] = True

    data_obj['queries'] = queries_list
    query_current = {
        "status": status,
        "title": data_obj['title'],
        "date": str(data_obj['date']),
        "message": data_obj['message'],
        "id": data_obj['id'],
        "specialist_id": data_obj['specialist']
    }
    data_obj['queryCurrent'] = query_current
    del data_obj['specialist']
    del data_obj['message']
    del data_obj['title']
    del data_obj['date']
    del data_obj['id']

    # main_node = "messagesList/specialist/{}/{}"
    db.child("messagesList/specialist/").child(
        node_specialist).child(node_client).set(data_obj)


def chosen_plan(client_id, data):
    node = Params.PREFIX['client'] + str(client_id)
    """Actualizar el plan elegido por cliente."""
    res = db.child("chosenPlans").child(node).update(data)
    return res


def mark_failed_file(room, message_id):
    """Actualizar que el archivo se ha subido a firebase."""
    node = 'chats/' + room + '/' + Params.PREFIX['message'] + str(message_id)

    if exist_node(node):
        db.child(node).update({"uploaded": 5})
        if DEBUG_FIREBASE:
            check_type_data('chats', node)
    else:
        logger.warning("mark_failed_file, nodo no existe:" + node)


def mark_uploaded_file(room, message_id, data):
    """Actualizar que el archivo se ha subido a firebase."""
    node = 'chats/' + room + '/' + Params.PREFIX['message'] + str(message_id)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    if exist_node(node):
        db.child(node).update(data)
        if DEBUG_FIREBASE:
            check_type_data('chats', node)
    else:
        logger.warning("mark_uploaded_file, nodo no existe:" + node)


def generateDataMessageClients(client_id, category_id, query_id,
                               status, specialist_id):
    # Luego se busca el titulo y su id de la consulta
    lista = SpecialistMessageListCustom(client_id, category_id)

    queries_list = PendingQueriesList(client_id, specialist_id)

    return createListMessageClients(lista.data, query_id, status,
                                    client_id, specialist_id, queries_list)


def SpecialistMessageListCustom(client_id, category_id):
    # Se llama al store procedure
    data_set = SpecialistMessageList_sp.search(2, client_id,
                                               category_id, 0, "")

    # El queryset se pasa serializer para mapear datos
    return SpecialistMessageListCustomSerializer(data_set, many=True)


def PendingQueriesList(client_id, specialist_id):
    mess = Message.objects.filter(query=OuterRef("pk"))\
                                  .order_by('-created_at')[:1]

    data_queries = Query.objects.values('id', 'title', 'status', 'specialist')\
                                .annotate(
                                    message=Subquery(
                                        mess.values('message')))\
                                .annotate(
                                    date_at=Subquery(
                                        mess.values('created_at')))\
                                .filter(client=client_id,
                                        specialist=specialist_id,
                                        status=1)\
                                .annotate(count=Count('id'))\
                                .order_by('-message__created_at')

    query_pending = PendingQueriesSerializer(data_queries, many=True)
    queries_list = {Params.PREFIX['query']+str(l['id']): l for l in query_pending.data}
    return queries_list


def delete_actual_plan_client(client_id):
    """Elimina nodo de plan de clientes"""
    node_client = Params.PREFIX['client'] + str(client_id)
    res = db.child("chosenPlans").child(node_client).remove()
    return res
