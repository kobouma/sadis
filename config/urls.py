# config/urls.py
from config.admin_site import *  
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def ping(request):
    return JsonResponse({"status": "ok", "service": "SADIS API"})


urlpatterns = [
    path("ping/",                 ping),
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