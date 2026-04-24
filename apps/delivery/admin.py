# apps/delivery/admin.py
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from apps.delivery.models import DeliveryTicket, DeliveryRate, TicketStatusHistory


class TicketStatusHistoryInline(TabularInline):
    model           = TicketStatusHistory
    extra           = 0
    readonly_fields = ["old_status", "new_status", "changed_by", "note", "created_at"]


@admin.register(DeliveryTicket)
class DeliveryTicketAdmin(ModelAdmin):
    inlines         = [TicketStatusHistoryInline]
    list_display    = ["id", "order", "agent", "delivery_type_badge",
                       "status_badge", "pickup_quartier",
                       "delivery_quartier", "fee_display", "created_at"]
    list_filter     = ["status", "delivery_type"]
    search_fields   = ["order__id", "agent__phone",
                       "pickup_quartier", "delivery_quartier"]
    readonly_fields = ["id", "assigned_at", "picked_up_at",
                       "delivered_at", "created_at"]
    list_per_page   = 25
    actions         = ["mark_assigned", "mark_picked", "mark_delivered"]

    fieldsets = (
        ("Commande",  {"fields": ("id", "order", "agent", "status", "delivery_type")}),
        ("Collecte",  {"fields": ("pickup_address", "pickup_quartier")}),
        ("Livraison", {"fields": ("delivery_address", "delivery_quartier", "fee")}),
        ("Position",  {"fields": ("agent_latitude", "agent_longitude")}),
        ("Dates",     {"fields": ("assigned_at", "picked_up_at",
                                   "delivered_at", "created_at")}),
        ("Notes",     {"fields": ("notes",)}),
    )

    STATUS_COLORS = {
        "pending":   ("#E3F2FD", "#1565C0"),
        "assigned":  ("#FFF3E0", "#E65100"),
        "picked_up": ("#EDE7F6", "#4527A0"),
        "en_route":  ("#FFF8E1", "#F57F17"),
        "delivered": ("#E8F5E9", "#2E7D32"),
        "failed":    ("#FFEBEE", "#C62828"),
    }

    def status_badge(self, obj):
        bg, fg = self.STATUS_COLORS.get(obj.status, ("#F5F5F5", "#616161"))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            bg, fg, obj.get_status_display()
        )
    status_badge.short_description = "Statut"

    def delivery_type_badge(self, obj):
        if obj.delivery_type == "express":
            return format_html(
                '<span style="background:#FFF8E1;color:#F57F17;padding:2px 8px;'
                'border-radius:10px;font-size:11px;font-weight:700">⚡ Express</span>'
            )
        return format_html(
            '<span style="background:#E8F5E9;color:#2E7D32;padding:2px 8px;'
            'border-radius:10px;font-size:11px">📦 Standard</span>'
        )
    delivery_type_badge.short_description = "Type"

    def fee_display(self, obj):
        return format_html('<strong>{} XOF</strong>', f"{obj.fee:,.0f}")
    fee_display.short_description = "Frais"

    @admin.action(description="🛵 Marquer assigné")
    def mark_assigned(self, request, qs): qs.update(status="assigned")

    @admin.action(description="📦 Colis récupéré")
    def mark_picked(self, request, qs): qs.update(status="picked_up")

    @admin.action(description="✅ Marquer livré")
    def mark_delivered(self, request, qs): qs.update(status="delivered")


@admin.register(DeliveryRate)
class DeliveryRateAdmin(ModelAdmin):
    list_display  = ["standard_fee_display", "express_fee_display",
                     "is_active", "updated_at"]
    list_editable = ["is_active"]

    def standard_fee_display(self, obj):
        return format_html('{} XOF', f"{obj.standard_fee:,.0f}")
    standard_fee_display.short_description = "Standard"

    def express_fee_display(self, obj):
        return format_html('<strong>{} XOF</strong>', f"{obj.express_fee:,.0f}")
    express_fee_display.short_description = "Express"