from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.delivery.models import DeliveryTicket
from apps.delivery.serializers import DeliveryTicketSerializer
from core.utils.response import success, error
from apps.users.permissions import IsDeliveryAgent

VALID_TRANSITIONS = {
    "claimed":    ["available"],
    "picked_up":  ["claimed"],
    "delivering": ["picked_up"],
    "delivered":  ["delivering"],
    "failed":     ["claimed", "picked_up", "delivering"],
}

class DeliveryTicketViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = DeliveryTicketSerializer
    permission_classes = [IsAuthenticated, IsDeliveryAgent]

    def get_queryset(self):
        return DeliveryTicket.objects.select_related("order","agent").prefetch_related("history")

    def list(self, request, *args, **kwargs):
        city = getattr(request.user.profile, "city", "")
        qs = self.get_queryset().filter(status=DeliveryTicket.Status.AVAILABLE,
                                        delivery_city__icontains=city)
        return success(data=self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=["get"])
    def mine(self, request):
        qs = self.get_queryset().filter(agent=request.user).exclude(
            status__in=[DeliveryTicket.Status.DELIVERED, DeliveryTicket.Status.FAILED])
        return success(data=self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=["post"])
    def claim(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status != DeliveryTicket.Status.AVAILABLE:
            return error("Ce ticket n'est plus disponible.")
        old = ticket.status
        ticket.agent, ticket.status, ticket.claimed_at = request.user, DeliveryTicket.Status.CLAIMED, timezone.now()
        ticket.save()
        TicketStatusHistory.objects.create(ticket=ticket, old_status=old,
                                           new_status=ticket.status, changed_by=request.user)
        return success(data=self.get_serializer(ticket).data, message="Ticket pris en charge.")

    @action(detail=True, methods=["post"], url_path="status")
    def update_status(self, request, pk=None):
        ticket     = self.get_object()
        new_status = request.data.get("status")
        note       = request.data.get("note", "")
        if ticket.agent != request.user:
            return error("Ce ticket ne vous est pas assigné.", status_code=status.HTTP_403_FORBIDDEN)
        if ticket.status not in VALID_TRANSITIONS.get(new_status, []):
            return error(f"Transition {ticket.status} → {new_status} non autorisée.")
        old = ticket.status
        ticket.status = new_status
        if new_status == DeliveryTicket.Status.DELIVERED:
            ticket.delivered_at = timezone.now()
        ticket.save()
        TicketStatusHistory.objects.create(ticket=ticket, old_status=old,
                                           new_status=new_status, changed_by=request.user, note=note)
        return success(data=self.get_serializer(ticket).data, message="Statut mis à jour.")
