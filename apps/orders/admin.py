# apps/orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from apps.orders.models import Order


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display    = ["id_short", "buyer", "shop", "product_name",
                       "quantity", "total_display", "delivery_type_badge",
                       "status_badge", "status", "created_at"]
    list_filter     = ["status", "delivery_type", "shop"]
    search_fields   = ["id", "buyer__phone", "shop__name", "product_name"]
    readonly_fields = ["id", "created_at", "shipped_at"]
    list_editable   = ["status"]
    list_per_page   = 25
    actions         = ["mark_paid", "mark_preparing", "mark_cancelled"]

    STATUS_COLORS = {
        "pending":    ("#FFF3E0", "#E65100"),
        "paid":       ("#E3F2FD", "#1565C0"),
        "preparing":  ("#EDE7F6", "#4527A0"),
        "shipped":    ("#FFF8E1", "#F57F17"),
        "delivering": ("#E8EAF6", "#283593"),
        "delivered":  ("#E8F5E9", "#2E7D32"),
        "cancelled":  ("#FFEBEE", "#C62828"),
        "disputed":   ("#FCE4EC", "#880E4F"),
    }
    STATUS_LABELS = {
        "pending": "En attente", "paid": "Payé",
        "preparing": "Préparation", "shipped": "Expédié",
        "delivering": "En livraison", "delivered": "Livré",
        "cancelled": "Annulé", "disputed": "Litige",
    }

    fieldsets = (
        ("Commande",  {"fields": ("id", "buyer", "shop", "status")}),
        ("Produit",   {"fields": ("product", "product_name", "variant_label",
                                   "unit_price", "quantity", "total_amount")}),
        ("Livraison", {"fields": ("delivery_type", "delivery_address",
                                   "delivery_city", "delivery_fee", "shipped_at")}),
        ("Autre",     {"fields": ("conversation", "notes", "created_at")}),
    )

    def id_short(self, obj):
        return str(obj.id)[:8].upper()
    id_short.short_description = "ID"

    def status_badge(self, obj):
        bg, fg = self.STATUS_COLORS.get(obj.status, ("#F5F5F5", "#616161"))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            bg, fg, self.STATUS_LABELS.get(obj.status, obj.status)
        )
    status_badge.short_description = "Statut"

    def delivery_type_badge(self, obj):
        if obj.delivery_type == "express":
            return format_html(
                '<span style="background:#FFF8E1;color:#F57F17;padding:2px 8px;'
                'border-radius:10px;font-size:11px;font-weight:700">⚡ Express</span>'
            )
        elif obj.delivery_type == "standard":
            return format_html(
                '<span style="background:#E8F5E9;color:#2E7D32;padding:2px 8px;'
                'border-radius:10px;font-size:11px">📦 Standard</span>'
            )
        return "—"
    delivery_type_badge.short_description = "Livraison"

    def total_display(self, obj):
        return format_html('<strong>{} XOF</strong>', f"{obj.total_amount:,.0f}")
    total_display.short_description = "Total"

    @admin.action(description="💳 Marquer Payé")
    def mark_paid(self, request, qs): qs.update(status="paid")

    @admin.action(description="📦 En préparation")
    def mark_preparing(self, request, qs): qs.update(status="preparing")

    @admin.action(description="❌ Annuler")
    def mark_cancelled(self, request, qs): qs.update(status="cancelled")