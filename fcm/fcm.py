"""Funcionamiento de Firebase Cloud Messaging."""
from pyfcm import FCMNotification
from .apps import FcmConfig


class Notification:
    """FCM."""

    def fcm_send_data(user_id, data=None):
        """Funcion para enviar mensaje a traves de topicos en Firebase."""
        # Notificaciones push para dispositivos moviles
        # manejamos 2 funciones para cada plataforma  en  especifico.
        api_key = FcmConfig.FCM_SETTINGS.get("FCM_SERVER_KEY")
        # topico para android
        topic = "user-"+str(user_id)
        # topico para IOS
        topic_ios = "ios-user-"+str(user_id)
        title_ios = data["title"]
        body_ios = data["body"]
        # configuracion de apikey
        push = FCMNotification(api_key=api_key)
        # funcion para enviar a android, con data_message
        result = push.notify_topic_subscribers(topic_name=topic,
                                               data_message=data)
        # funcion para enviar a IOS, con  notification message
        result_ios = push.notify_topic_subscribers(
            topic_name=topic_ios, message_title=title_ios,
            message_body=body_ios, data_message=data, badge=data["badge"])
        # do not raise errors, pyfcm will raise exceptions if response
        # status will # be anything but 200
        # import pdb; pdb.set_trace()
        print(user_id)
        print(data)
        print(body_ios)
        print(result)
        print(result_ios)
        return result
