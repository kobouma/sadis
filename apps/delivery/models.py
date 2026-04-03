import uuid
from django.db import models
from apps.users.models import User
from apps.orders.models import Order

class DeliveryTicket(models.Model):
    class Status(models.TextChoices):
        AVAILABLE  = "available",  "Disponible"
        CLAIMED    = "claimed",    "Pris en charge"
        PICKED_UP  = "picked_up",  "Récupéré"
        DELIVERING = "delivering", "En livraison"
        DELIVERED  = "delivered",  "Livré"
        FAILED     = "failed",     "Échec"

    id    = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="delivery_ticket")
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="delivery_tickets",
                              limit_choices_to={"role": "delivery"})
    status           = models.CharField(max_length=20, choices=Status.choices,
                                        default=Status.AVAILABLE, db_index=True)
    delivery_address = models.TextField()
    delivery_city    = models.CharField(max_length=100)
    agent_latitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    agent_longitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fee          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes        = models.TextField(blank=True)
    claimed_at   = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Ticket de livraison"
        verbose_name_plural = "Tickets de livraison"
        ordering            = ["-created_at"]

    def __str__(self): return f"Ticket {str(self.id)[:8]} — {self.status}"

class TicketStatusHistory(models.Model):
    ticket     = models.ForeignKey(DeliveryTicket, on_delete=models.CASCADE, related_name="history")
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note       = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]