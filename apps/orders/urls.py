# apps/orders/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BuyNowView, OrderViewSet

router = DefaultRouter()
router.register(r"", OrderViewSet, basename="order")

urlpatterns = [
    path("buy/", BuyNowView.as_view(), name="buy-now"),  # ← achat direct
    path("",     include(router.urls)),
]