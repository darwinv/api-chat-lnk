"""Funcionamiento de Firebase Cloud Messaging."""
from pyfcm import FCMNotification
from .apps import FcmConfig


class Notification:
    """FCM."""

    def fcm_send_data(user_id, data=None):
        """Funcion para enviar mensaje a traves de topicos en Firebase."""
        api_key = FcmConfig.FCM_SETTINGS.get("FCM_SERVER_KEY")
        push = FCMNotification(api_key=api_key)
        result = push.notify_topic_subscribers(topic_name=user_id,
                                               data_message=data)
        # do not raise errors, pyfcm will raise exceptions if response
        # status will # be anything but 200
        return result
