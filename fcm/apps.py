from django.apps import AppConfig


class FcmConfig(AppConfig):
    """Configuration of app."""
# cargarconfiguracion del settings secret
    name = 'fcm'
    FCM_SETTINGS = {
     "FCM_SERVER_KEY": "AIzaSyBFp1b8qmoSn13YFbpfTf3cIVgmjd_SCrY",
     "FCM_SERVER": "https://fcm.googleapis.com/fcm/send",
    }
