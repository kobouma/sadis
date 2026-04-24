from rest_framework import serializers

from apps.delivery.models import DeliveryTicket, TicketStatusHistory

class TicketStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.full_name", read_only=True)
    class Meta:
        model  = TicketStatusHistory
        fields = ["old_status", "new_status", "changed_by_name", "note", "created_at"]

class DeliveryTicketSerializer(serializers.ModelSerializer):
    history    = TicketStatusHistorySerializer(many=True, read_only=True)
    agent_name = serializers.CharField(source="agent.full_name", read_only=True, default=None)
    order_id   = serializers.UUIDField(source="order.id", read_only=True)
    class Meta:
        model  = DeliveryTicket
        fields = ["id", "order_id", "status", "agent_name",
                  "delivery_address", "delivery_city",
                  "agent_latitude", "agent_longitude",
                  "fee", "notes", "claimed_at", "delivered_at", "created_at", "history"]
        read_only_fields = ["id", "order_id", "claimed_at", "delivered_at", "created_at"]
