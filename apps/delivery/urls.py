from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.delivery.views import DeliveryTicketViewSet
router = DefaultRouter()
router.register(r"tickets", DeliveryTicketViewSet, basename="delivery-ticket")
urlpatterns = [path("", include(router.urls))]
