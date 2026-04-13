# apps/orders/serializers.py
from rest_framework import serializers
from apps.orders.models import Order
from apps.products.models import Product, ProductVariant


class BuyNowSerializer(serializers.Serializer):
    """
    Achat direct — un seul produit, pas de panier.
    POST /orders/buy/
    """
    product_id       = serializers.UUIDField()
    variant_id       = serializers.IntegerField(required=False, allow_null=True)
    quantity         = serializers.IntegerField(default=1, min_value=1)
    delivery_address = serializers.CharField()
    delivery_city    = serializers.CharField()
    notes            = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data):
        # Valider produit
        try:
            product = Product.objects.select_related("shop").get(
                pk=data["product_id"], is_available=True
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produit introuvable ou indisponible.")

        # Vérifier stock
        if product.stock < data["quantity"]:
            raise serializers.ValidationError(
                f"Stock insuffisant. Disponible : {product.stock}"
            )

        # Valider variante
        variant = None
        if data.get("variant_id"):
            try:
                variant = ProductVariant.objects.get(
                    pk=data["variant_id"], product=product, is_available=True
                )
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Variante introuvable.")

        # L'acheteur ne peut pas acheter son propre produit
        buyer = self.context["request"].user
        if product.shop.owner == buyer:
            raise serializers.ValidationError(
                "Vous ne pouvez pas acheter votre propre produit."
            )

        data["product"] = product
        data["variant"] = variant
        return data


class OrderSerializer(serializers.ModelSerializer):
    buyer_name  = serializers.CharField(source="buyer.full_name", read_only=True)
    shop_name   = serializers.CharField(source="shop.name",       read_only=True)
    shop_slug   = serializers.CharField(source="shop.slug",       read_only=True)
    subtotal    = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model  = Order
        fields = [
            "id", "status", "buyer_name", "shop_name", "shop_slug",
            "product_name", "variant_label", "unit_price", "quantity",
            "subtotal", "total_amount",
            "delivery_type", "delivery_address", "delivery_city", "delivery_fee",
            "notes", "shipped_at", "created_at",
        ]
        read_only_fields = ["id", "total_amount", "created_at", "shipped_at"]