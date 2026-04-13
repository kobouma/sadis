import uuid
from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from apps.users.models import User


class ShopCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name        = "Catégorie de boutique"
        verbose_name_plural = "Catégories de boutiques"
        ordering            = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Shop(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner       = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name="shops",
                                    )
    category    = models.ForeignKey(ShopCategory, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name="shops")
    name        = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)

    # ── Cloudinary : remplace ImageField ─────────────────────
    logo   = CloudinaryField("logo",   folder="sadis/shops/logos",
                             blank=True, null=True)
    banner = CloudinaryField("banner", folder="sadis/shops/banners",
                             blank=True, null=True)

    phone      = models.CharField(max_length=20, blank=True)
    city       = models.CharField(max_length=100, blank=True)
    address    = models.TextField(blank=True)
    latitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active  = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Boutique"
        verbose_name_plural = "Boutiques"
        ordering            = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while Shop.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.owner.full_name})"