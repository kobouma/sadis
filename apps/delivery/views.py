# apps/delivery/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.delivery.models import DeliveryTicket
from apps.delivery.serializers import DeliveryTicketSerializer
from apps.users.permissions import IsDeliveryAgent
from core.utils.response import success, error


class DeliveryTicketViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoints livreur :
    GET  /delivery/tickets/          → tickets disponibles dans ma zone
    GET  /delivery/tickets/<id>/     → détail ticket
    POST /delivery/tickets/<id>/claim/    → prendre en charge
    POST /delivery/tickets/<id>/pickup/  → colis récupéré
    POST /delivery/tickets/<id>/deliver/ → livré
    """
    serializer_class   = DeliveryTicketSerializer
    permission_classes = [IsAuthenticated, IsDeliveryAgent]

    def get_queryset(self):
        user = self.request.user
        # Tickets disponibles OU assignés à ce livreur
        return DeliveryTicket.objects.filter(
            status__in=["pending", "assigned", "picked_up", "en_route"]
        ).select_related("order__buyer", "order__shop", "agent")

    def list(self, request, *args, **kwargs):
        # Filtrer par type de livraison si demandé
        qs = self.get_queryset()
        dtype = request.query_params.get("type")
        if dtype in ["standard", "express"]:
            qs = qs.filter(delivery_type=dtype)
        # Priorité : tickets non assignés d'abord
        qs = qs.order_by("status", "-created_at")
        return success(data=self.get_serializer(qs, many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return success(data=self.get_serializer(self.get_object()).data)

    @action(detail=True, methods=["post"])
    def claim(self, request, pk=None):
        """Le livreur prend en charge le ticket."""
        ticket = self.get_object()
        if ticket.status != "pending":
            return error("Ce ticket est déjà pris en charge.")
        if ticket.agent is not None:
            return error("Ce ticket a déjà un livreur.")

        from apps.orders.shipping_service import assign_agent
        assign_agent(ticket, request.user)
        return success(
            data    = self.get_serializer(ticket).data,
            message = "Ticket pris en charge ✅"
        )

    @action(detail=True, methods=["post"])
    def pickup(self, request, pk=None):
        """Le livreur confirme avoir récupéré le colis."""
        ticket = self.get_object()
        if ticket.agent != request.user:
            return error("Vous n'êtes pas le livreur de ce ticket.", status_code=403)
        if ticket.status != "assigned":
            return error("Le colis n'est pas encore assigné.")

        from apps.orders.shipping_service import mark_picked_up
        mark_picked_up(ticket, request.user)
        return success(message="Colis récupéré ✅")

    @action(detail=True, methods=["post"])
    def deliver(self, request, pk=None):
        """Le livreur confirme la livraison."""
        ticket = self.get_object()
        if ticket.agent != request.user:
            return error("Vous n'êtes pas le livreur de ce ticket.", status_code=403)
        if ticket.status != "picked_up":
            return error("Le colis n'a pas encore été récupéré.")

        from apps.orders.shipping_service import mark_delivered
        mark_delivered(ticket, request.user)
        return success(message="Livraison confirmée ✅")