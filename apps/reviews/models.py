import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User
from apps.products.models import Product

class Like(models.Model):
    user       = models.ForeignKey(User,    on_delete=models.CASCADE, related_name="likes")
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name    = "Like"
        unique_together = [["user", "product"]]
        ordering        = ["-created_at"]
    def __str__(self): return f"{self.user.full_name} ❤ {self.product.name}"

class Review(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(User,    on_delete=models.CASCADE, related_name="reviews")
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating     = models.PositiveSmallIntegerField(
                    validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name        = "Avis"
        verbose_name_plural = "Avis"
        unique_together     = [["user", "product"]]
        ordering            = ["-created_at"]
    def __str__(self): return f"{self.user.full_name} — {self.product.name} ({self.rating}★)"

def review_image_path(instance, filename):
    return f"reviews/{instance.review.id}/{filename}"

class ReviewImage(models.Model):
    review     = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="images")
    image      = models.ImageField(upload_to=review_image_path)
    order      = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Photo d'avis"
        ordering     = ["order"]

class ReviewReply(models.Model):
    review     = models.OneToOneField(Review, on_delete=models.CASCADE, related_name="reply")
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="review_replies")
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Réponse à un avis"
