import uuid
from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import User
from apps.products.models import Product, ProductVariant
from apps.shops.models import Shop

class Cart(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Panier"
    def __str__(self): return f"Panier de {self.user.full_name}"
    @property
    def total(self): return sum(item.subtotal for item in self.items.all())
    @property
    def item_count(self): return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant  = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    class Meta:
        verbose_name    = "Ligne de panier"
        unique_together = [["cart", "product", "variant"]]
    @property
    def unit_price(self):
        base = self.product.price
        if self.variant: base += self.variant.extra_price
        return base
    @property
    def subtotal(self): return self.unit_price * self.quantity

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING    = "pending",    "En attente"
        PAID       = "paid",       "Payé"
        DELIVERING = "delivering", "En livraison"
        DELIVERED  = "delivered",  "Livré"
        DISPUTED   = "disputed",   "Litige"
        REFUNDED   = "refunded",   "Remboursé"
        CANCELLED  = "cancelled",  "Annulé"

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer          = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    shop           = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name="orders")
    status         = models.CharField(max_length=20, choices=Status.choices,
                                      default=Status.PENDING, db_index=True)
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2,
                                         validators=[MinValueValidator(0)])
    delivery_address = models.TextField(blank=True)
    delivery_city    = models.CharField(max_length=100, blank=True)
    conversation     = models.OneToOneField("chat.Conversation", on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name="order")
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name        = "Commande"
        verbose_name_plural = "Commandes"
        ordering            = ["-created_at"]
    def __str__(self): return f"Commande #{str(self.id)[:8]}"

class OrderItem(models.Model):
    order         = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product       = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    product_name  = models.CharField(max_length=255)
    variant_label = models.CharField(max_length=100, blank=True)
    unit_price    = models.DecimalField(max_digits=12, decimal_places=2)
    quantity      = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    class Meta:
        verbose_name = "Ligne de commande"
    @property
    def subtotal(self): return self.unit_price * self.quantity
