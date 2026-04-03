from django.contrib import admin

from apps.delivery.models import DeliveryTicket, TicketStatusHistory

class TicketStatusHistoryInline(admin.TabularInline):
    model           = TicketStatusHistory; extra = 0
    readonly_fields = ["old_status", "new_status", "changed_by", "note", "created_at"]

@admin.register(DeliveryTicket)
class DeliveryTicketAdmin(admin.ModelAdmin):
    inlines         = [TicketStatusHistoryInline]
    list_display    = ["id", "order", "agent", "status", "delivery_city", "created_at"]
    list_filter     = ["status", "delivery_city"]
    search_fields   = ["order__id", "agent__phone"]
    readonly_fields = ["id", "claimed_at", "delivered_at", "created_at"]
