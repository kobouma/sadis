from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.orders.views import CartItemView, CartView, OrderViewSet
router = DefaultRouter()
router.register(r"", OrderViewSet, basename="order")
urlpatterns = [
    path("cart/",                    CartView.as_view(),               name="cart"),
    path("cart/items/",              CartItemView.as_view(),            name="cart-items"),
    path("cart/items/<int:item_id>/", CartItemView.as_view(),           name="cart-item-detail"),
    path("",                         include(router.urls)),
]
