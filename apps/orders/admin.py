from django.contrib import admin

from apps.orders.models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model  = CartItem; extra = 0
    fields = ["product", "variant", "quantity"]

class OrderItemInline(admin.TabularInline):
    model           = OrderItem; extra = 0
    readonly_fields = ["product_name", "variant_label", "unit_price", "quantity"]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines       = [CartItemInline]
    list_display  = ["user", "item_count", "total", "updated_at"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines         = [OrderItemInline]
    list_display    = ["id", "buyer", "shop", "status", "total_amount", "created_at"]
    list_filter     = ["status"]
    readonly_fields = ["id", "created_at"]
    list_editable   = ["status"]
