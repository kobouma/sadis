import uuid
from django.db import models
from apps.users.models import User

class Notification(models.Model):
    class Type(models.TextChoices):
        ORDER_PLACED     = "order_placed",     "Commande reçue"
        PAYMENT_RECEIVED = "payment_received", "Paiement reçu"
        ESCROW_HELD      = "escrow_held",      "Fonds bloqués"
        ESCROW_RELEASED  = "escrow_released",  "Fonds libérés"
        DELIVERY_UPDATE  = "delivery_update",  "Mise à jour livraison"
        CHAT_MESSAGE     = "chat_message",     "Nouveau message"
        DISPUTE_OPENED   = "dispute_opened",   "Litige ouvert"
        SYSTEM           = "system",           "Système"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notif_type = models.CharField(max_length=30, choices=Type.choices, db_index=True)
    title      = models.CharField(max_length=200)
    body       = models.TextField()
    data       = models.JSONField(default=dict)
    is_read    = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name        = "Notification"
        verbose_name_plural = "Notifications"
        ordering            = ["-created_at"]
