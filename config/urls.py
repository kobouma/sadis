from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/",                admin.site.urls),
    path("api/v1/auth/",          include("apps.users.urls")),
    path("api/v1/shops/",         include("apps.shops.urls")),
    path("api/v1/products/",      include("apps.products.urls")),
    path("api/v1/orders/",        include("apps.orders.urls")),
    path("api/v1/delivery/",      include("apps.delivery.urls")),
    path("api/v1/chat/",          include("apps.chat.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/reviews/",       include("apps.reviews.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


"""
config/asgi.py
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from core.middleware.jwt import JwtAuthMiddleware
from apps.chat.routing import chat_websocket_urlpatterns
from apps.tracking.routing import tracking_websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddleware(
        URLRouter(chat_websocket_urlpatterns + tracking_websocket_urlpatterns)
    ),
})