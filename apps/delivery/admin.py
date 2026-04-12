# apps/delivery/admin.py
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from apps.delivery.models import DeliveryTicket, TicketStatusHistory


class TicketStatusHistoryInline(TabularInline):
    model           = TicketStatusHistory
    extra           = 0
    readonly_fields = ["old_status", "new_status", "changed_by", "note", "created_at"]


@admin.register(DeliveryTicket)
class DeliveryTicketAdmin(ModelAdmin):
    inlines         = [TicketStatusHistoryInline]
    list_display    = ["id", "order", "agent", "status_badge", "delivery_city", "created_at"]
    list_filter     = ["status", "delivery_city"]
    search_fields   = ["order__id", "agent__phone"]
    readonly_fields = ["id", "claimed_at", "delivered_at", "created_at"]
    list_per_page   = 25
    actions         = ["mark_assigned", "mark_picked", "mark_delivered"]

    STATUS_COLORS = {
        "pending":    ("#FFF3E0", "#E65100"),
        "assigned":   ("#E3F2FD", "#1565C0"),
        "picked_up":  ("#EDE7F6", "#4527A0"),
        "in_transit": ("#FFF8E1", "#F57F17"),
        "delivered":  ("#E8F5E9", "#2E7D32"),
        "failed":     ("#FFEBEE", "#C62828"),
    }

    def status_badge(self, obj):
        bg, fg = self.STATUS_COLORS.get(obj.status, ("#F5F5F5", "#616161"))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            bg, fg, obj.status
        )
    status_badge.short_description = "Statut"

    @admin.action(description="📦 Assigner")
    def mark_assigned(self, request, qs): qs.update(status="assigned")

    @admin.action(description="🏃 Récupéré")
    def mark_picked(self, request, qs): qs.update(status="picked_up")

    @admin.action(description="✅ Livré")
    def mark_delivered(self, request, qs): qs.update(status="delivered")