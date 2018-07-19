from django.apps import AppConfig
from linkupapi.settings_secret import CONFIG_ENVIROMENT


class FcmConfig(AppConfig):
    """Configuration of app."""
# cargar configuracion del settings secret
    name = 'fcm'
    FCM_SETTINGS = {
     "FCM_SERVER_KEY": CONFIG_ENVIROMENT["fcmServerKey"],
     "FCM_SERVER": "https://fcm.googleapis.com/fcm/send",
    }
