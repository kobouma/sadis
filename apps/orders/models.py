# apps/orders/models.py
# Modèle C2C — achat direct, pas de panier

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import User
from apps.products.models import Product, ProductVariant
from apps.shops.models import Shop


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING    = "pending",    "En attente de paiement"
        PAID       = "paid",       "Payé"
        PREPARING  = "preparing",  "En préparation"
        SHIPPED    = "shipped",    "Expédié"
        DELIVERING = "delivering", "En livraison"
        DELIVERED  = "delivered",  "Livré"
        DISPUTED   = "disputed",   "Litige"
        REFUNDED   = "refunded",   "Remboursé"
        CANCELLED  = "cancelled",  "Annulé"

    class DeliveryType(models.TextChoices):
        STANDARD = "standard", "Standard (24-48h)"
        EXPRESS  = "express",  "Express (2-4h)"

    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer   = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    shop    = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.PROTECT,
                                 null=True, related_name="orders")

    # ── Produit snapshoté au moment de la commande ────────────
    product_name  = models.CharField(max_length=255)
    variant_label = models.CharField(max_length=100, blank=True)
    unit_price    = models.DecimalField(max_digits=12, decimal_places=2)
    quantity      = models.PositiveIntegerField(default=1,
                                                validators=[MinValueValidator(1)])
    total_amount  = models.DecimalField(max_digits=12, decimal_places=2,
                                         validators=[MinValueValidator(0)])

    # ── Livraison ──────────────────────────────────────────────
    status           = models.CharField(max_length=20, choices=Status.choices,
                                         default=Status.PENDING, db_index=True)
    delivery_type    = models.CharField(max_length=20, choices=DeliveryType.choices,
                                         blank=True, default="")
    delivery_address = models.TextField(blank=True)
    delivery_city    = models.CharField(max_length=100, blank=True)
    delivery_fee     = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ── Relations ──────────────────────────────────────────────
    conversation = models.OneToOneField(
        "chat.Conversation", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="order"
    )
    notes      = models.TextField(blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Commande"
        verbose_name_plural = "Commandes"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"Commande #{str(self.id)[:8]} — {self.product_name}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity