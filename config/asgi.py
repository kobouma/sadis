# config/asgi.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

# ← Django doit être configuré AVANT tout import de modèles ou middleware
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from core.middleware.jwt import JwtAuthMiddleware
from apps.chat.routing import chat_websocket_urlpatterns
from apps.tracking.routing import tracking_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddleware(
        URLRouter(chat_websocket_urlpatterns + tracking_websocket_urlpatterns)
    ),
})