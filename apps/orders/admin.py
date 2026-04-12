# apps/orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from apps.orders.models import Cart, CartItem, Order, OrderItem


class CartItemInline(TabularInline):
    model  = CartItem
    extra  = 0
    fields = ["product", "variant", "quantity"]


class OrderItemInline(TabularInline):
    model           = OrderItem
    extra           = 0
    readonly_fields = ["product_name", "variant_label", "unit_price", "quantity", "subtotal"]

    def subtotal(self, obj):
        return format_html(
            '<strong>{} XOF</strong>',
            f"{obj.unit_price * obj.quantity:,.0f}"
        )
    subtotal.short_description = "Sous-total"


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    inlines      = [CartItemInline]
    list_display = ["user", "item_count", "total_display", "updated_at"]

    def total_display(self, obj):
        return format_html('<strong>{} XOF</strong>', f"{obj.total:,.0f}")
    total_display.short_description = "Total"


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    inlines         = [OrderItemInline]
    list_display    = ["id", "buyer", "shop", "status_badge", "status",
                       "total_display", "created_at"]
    list_filter     = ["status", "shop"]
    search_fields   = ["id", "buyer__phone", "shop__name"]
    readonly_fields = ["id", "created_at"]
    list_editable   = ["status"]
    list_per_page   = 25
    actions         = ["mark_paid", "mark_delivering", "mark_delivered", "mark_cancelled"]

    STATUS_COLORS = {
        "pending":    ("#FFF3E0", "#E65100"),
        "paid":       ("#E3F2FD", "#1565C0"),
        "delivering": ("#EDE7F6", "#4527A0"),
        "delivered":  ("#E8F5E9", "#2E7D32"),
        "cancelled":  ("#FFEBEE", "#C62828"),
    }
    STATUS_LABELS = {
        "pending": "En attente", "paid": "Payé",
        "delivering": "En livraison", "delivered": "Livré", "cancelled": "Annulé",
    }

    def status_badge(self, obj):
        bg, fg = self.STATUS_COLORS.get(obj.status, ("#F5F5F5", "#616161"))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            bg, fg, self.STATUS_LABELS.get(obj.status, obj.status)
        )
    status_badge.short_description = "Statut"

    def total_display(self, obj):
        return format_html('<strong>{} XOF</strong>', f"{obj.total_amount:,.0f}")
    total_display.short_description = "Total"

    @admin.action(description="💳 Marquer comme Payé")
    def mark_paid(self, request, qs): qs.update(status="paid")

    @admin.action(description="🚚 Marquer En livraison")
    def mark_delivering(self, request, qs): qs.update(status="delivering")

    @admin.action(description="✅ Marquer comme Livré")
    def mark_delivered(self, request, qs): qs.update(status="delivered")

    @admin.action(description="❌ Annuler")
    def mark_cancelled(self, request, qs): qs.update(status="cancelled")