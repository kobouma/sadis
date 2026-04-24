# apps/orders/views.py
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.orders.serializers import BuyNowSerializer, OrderSerializer
from apps.orders.shipping_service import get_delivery_rates, ship_order
from core.utils.response import success, created, error


class BuyNowView(APIView):
    """
    POST /orders/buy/
    Achat direct — crée une commande immédiatement sans panier.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        s = BuyNowSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        data = s.validated_data

        product = data["product"]
        variant = data.get("variant")
        qty     = data["quantity"]

        # Prix unitaire
        unit_price = product.price
        if variant:
            unit_price += variant.extra_price

        # Créer la commande
        order = Order.objects.create(
            buyer            = request.user,
            shop             = product.shop,
            product          = product,
            product_name     = product.name,
            variant_label    = variant.label if variant else "",
            unit_price       = unit_price,
            quantity         = qty,
            total_amount     = unit_price * qty,
            delivery_address = data["delivery_address"],
            delivery_city    = data["delivery_city"],
            notes            = data.get("notes", ""),
            status           = Order.Status.PENDING,
        )

        # Décrémenter le stock
        product.stock -= qty
        product.save(update_fields=["stock"])

        # Notifier le vendeur
        _notify_seller_new_order(order)

        return created(
            data    = OrderSerializer(order).data,
            message = "Commande créée avec succès.",
        )


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /orders/         → mes commandes (acheteur + vendeur)
    GET /orders/<id>/    → détail commande
    GET /orders/<id>/delivery-options/ → tarifs livraison
    POST /orders/<id>/ship/            → vendeur expédie
    POST /orders/<id>/cancel/          → annuler
    """
    serializer_class   = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        as_buyer  = Order.objects.filter(buyer=user)
        as_seller = Order.objects.filter(shop__owner=user)
        qs = (as_buyer | as_seller).distinct().select_related(
            "buyer", "shop", "product"
        )
        s = self.request.query_params.get("status")
        if s:
            qs = qs.filter(status=s)
        role = self.request.query_params.get("role")
        if role == "buyer":
            qs = as_buyer
        elif role == "seller":
            qs = as_seller
        return qs.order_by("-created_at")

    def list(self, request, *args, **kwargs):
        return success(data=self.get_serializer(self.get_queryset(), many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return success(data=self.get_serializer(self.get_object()).data)

    @action(detail=True, methods=["get"], url_path="delivery-options")
    def delivery_options(self, request, pk=None):
        """Tarifs livraison + liste des quartiers de Ouagadougou."""
        order = self.get_object()
        if order.shop.owner != request.user:
            return error("Non autorisé.", status_code=403)
        if order.status not in [Order.Status.PAID, Order.Status.PREPARING]:
            return error("Commande non prête pour l'expédition.")

        from apps.orders.shipping_service import get_delivery_rates, get_quartiers
        return success(data={
            "order_id":   str(order.id),
            "options":    get_delivery_rates(),
            "quartiers":  get_quartiers(),
        })

    @action(detail=True, methods=["post"], url_path="ship")
    def ship(self, request, pk=None):
        """
        POST /orders/<id>/ship/
        {
          "delivery_type":   "standard" | "express",
          "pickup_address":  "Rue 10.45, secteur 15",
          "pickup_quartier": "Cissin"
        }
        """
        order = self.get_object()
        if order.shop.owner != request.user:
            return error("Seul le vendeur peut expédier.", status_code=403)

        delivery_type    = request.data.get("delivery_type", "standard")
        pickup_address   = request.data.get("pickup_address", "").strip()
        pickup_quartier  = request.data.get("pickup_quartier", "").strip()

        if delivery_type not in ["standard", "express"]:
            return error("Type invalide : 'standard' ou 'express'.")
        if not pickup_address:
            return error("L'adresse de collecte est requise.")
        if not pickup_quartier:
            return error("Le quartier de collecte est requis.")

        from apps.orders.shipping_service import ship_order
        try:
            result = ship_order(
                order           = order,
                delivery_type   = delivery_type,
                seller          = request.user,
                pickup_address  = pickup_address,
                pickup_quartier = pickup_quartier,
            )
            return success(data=result, message="Commande expédiée ✅")
        except ValueError as e:
            return error(str(e))