from rest_framework import serializers
from apps.orders.models import Cart, CartItem, Order, OrderItem
from apps.products.models import Product, ProductVariant
from apps.products.serializers import ProductListSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product    = ProductListSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    subtotal   = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model  = CartItem
        fields = ["id", "product", "product_id", "variant_id", "quantity", "unit_price", "subtotal"]
    def validate_product_id(self, value):
        try: return Product.objects.get(pk=value, is_available=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produit introuvable ou indisponible.")
    def validate_variant_id(self, value):
        if value is None: return None
        try: return ProductVariant.objects.get(pk=value, is_available=True)
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError("Variante introuvable.")
    def create(self, validated_data):
        product = validated_data.pop("product_id")
        variant = validated_data.pop("variant_id", None)
        cart    = validated_data.pop("cart")
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant,
            defaults={"quantity": validated_data.get("quantity", 1)})
        if not created:
            item.quantity += validated_data.get("quantity", 1)
            item.save()
        return item

class CartSerializer(serializers.ModelSerializer):
    items      = CartItemSerializer(many=True, read_only=True)
    total      = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    class Meta:
        model  = Cart
        fields = ["id", "items", "total", "item_count", "updated_at"]

class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model  = OrderItem
        fields = ["id", "product_name", "variant_label", "unit_price", "quantity", "subtotal"]

class OrderSerializer(serializers.ModelSerializer):
    items      = OrderItemSerializer(many=True, read_only=True)
    buyer_name = serializers.CharField(source="buyer.full_name", read_only=True)
    shop_name  = serializers.CharField(source="shop.name",       read_only=True)
    class Meta:
        model  = Order
        fields = ["id", "status", "total_amount",
                  "delivery_address", "delivery_city", "notes",
                  "buyer_name", "shop_name", "items", "created_at"]
        read_only_fields = ["id", "total_amount", "created_at"]