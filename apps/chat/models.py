import uuid
from django.db import models
from apps.users.models import User
from apps.products.models import Product

class MessageType(models.TextChoices):
    TEXT             = "text",             "Texte"
    IMAGE            = "image",            "Image"
    INVOICE          = "invoice",          "Facture"
    PAYMENT          = "payment",          "Paiement"
    ESCROW_HELD      = "escrow_held",      "Fonds bloqués"
    ESCROW_RELEASED  = "escrow_released",  "Fonds libérés"
    REFUND           = "refund",           "Remboursement"
    DELIVERY_REQUEST = "delivery_request", "Demande de livraison"
    DELIVERY_CONFIRM = "delivery_confirm", "Livraison confirmée"
    DISPUTE          = "dispute",          "Litige"
    LOCATION         = "location",         "Position GPS"
    SYSTEM           = "system",           "Système"

class ConversationStatus(models.TextChoices):
    OPEN     = "open",     "Ouverte"
    PAID     = "paid",     "Payée"
    ESCROW   = "escrow",   "En escrow"
    CLOSED   = "closed",   "Clôturée"
    DISPUTED = "disputed", "En litige"

class Conversation(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_as_buyer")
    seller  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_as_seller")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name="conversations")
    status        = models.CharField(max_length=20, choices=ConversationStatus.choices,
                                     default=ConversationStatus.OPEN, db_index=True)
    escrow_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name        = "Conversation"
        verbose_name_plural = "Conversations"
        ordering            = ["-updated_at"]
        unique_together     = [["buyer", "seller", "product"]]
    def __str__(self): return f"Chat {self.buyer.full_name} ↔ {self.seller.full_name}"

class Message(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    msg_type     = models.CharField(max_length=30, choices=MessageType.choices,
                                    default=MessageType.TEXT, db_index=True)
    payload      = models.JSONField(default=dict)
    is_read      = models.BooleanField(default=False, db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta:
        verbose_name = "Message"
        ordering     = ["created_at"]
        indexes      = [models.Index(fields=["conversation", "created_at"]),
                        models.Index(fields=["conversation", "is_read"])]