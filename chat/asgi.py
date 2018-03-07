"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
#from channels.routing import get_default_application # version 2.0
from channels.asgi import get_channel_layer # version 1.x


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "linkupapi.settings")
#django.setup() # version  2.0
#application = get_default_application() # version 2.0
channel_layer = get_channel_layer()
