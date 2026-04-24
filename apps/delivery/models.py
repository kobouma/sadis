# apps/delivery/models.py
import uuid
from django.db import models
from apps.users.models import User
from apps.orders.models import Order


class DeliveryTicket(models.Model):

    class Status(models.TextChoices):
        PENDING    = "pending",    "En attente d'un livreur"
        ASSIGNED   = "assigned",   "Livreur assigné"
        PICKED_UP  = "picked_up",  "Colis récupéré chez le vendeur"
        EN_ROUTE   = "en_route",   "En route vers l'acheteur"
        DELIVERED  = "delivered",  "Livré"
        FAILED     = "failed",     "Échec de livraison"

    class DeliveryType(models.TextChoices):
        STANDARD = "standard", "Standard (2-6h)"
        EXPRESS  = "express",  "Express (-2h)"

    id    = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE,
                                  related_name="delivery_ticket")
    agent = models.ForeignKey(User, on_delete=models.SET_NULL,
                               null=True, blank=True,
                               related_name="delivery_tickets",
                               limit_choices_to={"is_delivery": True})

    delivery_type = models.CharField(max_length=20, choices=DeliveryType.choices,
                                      default=DeliveryType.STANDARD)
    status        = models.CharField(max_length=20, choices=Status.choices,
                                      default=Status.PENDING, db_index=True)

    # ── Adresses ──────────────────────────────────────────────
    # Point de collecte (chez le vendeur)
    pickup_address  = models.TextField(verbose_name="Adresse de collecte")
    pickup_quartier = models.CharField(max_length=100, verbose_name="Quartier vendeur")

    # Point de livraison (chez l'acheteur)
    delivery_address  = models.TextField(verbose_name="Adresse de livraison")
    delivery_quartier = models.CharField(max_length=100, verbose_name="Quartier acheteur")

    # ── Position livreur en temps réel ────────────────────────
    agent_latitude  = models.DecimalField(max_digits=9, decimal_places=6,
                                           null=True, blank=True)
    agent_longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                           null=True, blank=True)

    fee          = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    notes        = models.TextField(blank=True)
    assigned_at  = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Ticket de livraison"
        verbose_name_plural = "Tickets de livraison"
        ordering            = ["-created_at"]

    def __str__(self):
        return (f"Ticket {str(self.id)[:8]} — "
                f"{self.pickup_quartier} → {self.delivery_quartier} "
                f"[{self.delivery_type}]")


class TicketStatusHistory(models.Model):
    ticket     = models.ForeignKey(DeliveryTicket, on_delete=models.CASCADE,
                                    related_name="history")
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note       = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


# ── Tarifs livraison Ouagadougou ──────────────────────────────
class DeliveryRate(models.Model):
    """
    Tarif unique pour Ouagadougou.
    Configurable depuis l'admin sans toucher au code.
    """
    standard_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    express_fee  = models.DecimalField(max_digits=10, decimal_places=2, default=2000)
    is_active    = models.BooleanField(default=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Tarif livraison Ouagadougou"
        verbose_name_plural = "Tarifs livraison"

    def __str__(self):
        return f"Standard: {self.standard_fee} XOF / Express: {self.express_fee} XOF"

    @classmethod
    def get_active(cls):
        rate = cls.objects.filter(is_active=True).first()
        if rate:
            return {"standard": float(rate.standard_fee),
                    "express":  float(rate.express_fee)}
        return {"standard": 1000.0, "express": 2000.0}