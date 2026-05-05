import uuid
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField
from apps.shops.models import Shop


class Category(models.Model):
    name   = models.CharField(max_length=100, unique=True)
    slug   = models.SlugField(max_length=120, unique=True, blank=True)
    icon   = models.CharField(max_length=10, blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="children")

    class Meta:
        verbose_name        = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering            = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop        = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name="products")
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=12, decimal_places=2,
                                      validators=[MinValueValidator(0)])
    old_price   = models.DecimalField(max_digits=12, decimal_places=2,
                                      null=True, blank=True,
                                      validators=[MinValueValidator(0)])
    stock        = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    views_count  = models.PositiveIntegerField(default=0, editable=False)
    sales_count  = models.PositiveIntegerField(default=0, editable=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Produit"
        verbose_name_plural = "Produits"
        ordering            = ["-created_at"]
        indexes = [
            models.Index(fields=["shop", "is_available"]),
            models.Index(fields=["category"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} — {self.shop.name}"

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0


class ProductImage(models.Model):
    class MediaType(models.TextChoices):
        PHOTO = "photo", "Photo"
        VIDEO = "video", "Vidéo"

    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")

    # ── Cloudinary : remplace FileField ──────────────────────
    # Stocke le public_id Cloudinary (ex: "sadis/products/mon-slug/img_0")
    file = CloudinaryField(
        "image",
        folder="sadis/products",
        blank=True,
        null=True,
        resource_type="auto",          # accepte photo ET vidéo
    )

    media_type = models.CharField(
        max_length=10, choices=MediaType.choices, default=MediaType.PHOTO
    )
    order    = models.PositiveSmallIntegerField(default=0)
    is_cover = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Média produit"
        ordering     = ["order"]

    def __str__(self):
        return f"Média #{self.order} — {self.product.name}"

    # ── URLs pratiques utilisées dans les serializers ─────────
    @property
    def url(self):
        """URL CDN Cloudinary — même mécanisme que card_url pour garantir une URL valide."""
        if not self.file:
            return None
        import cloudinary
        return cloudinary.CloudinaryImage(str(self.file)).build_url(
            quality="auto:good", fetch_format="auto",
        )

    @property
    def thumbnail_url(self):
        """Vignette 400×400 recadrée automatiquement."""
        if not self.file:
            return None
        import cloudinary
        return cloudinary.CloudinaryImage(str(self.file)).build_url(
            width=400, height=400,
            crop="fill", gravity="auto",
            quality="auto:good", fetch_format="auto",
        )

    @property
    def card_url(self):
        """Image 600px de large, optimisée pour les cards Flutter."""
        if not self.file:
            return None
        import cloudinary
        return cloudinary.CloudinaryImage(str(self.file)).build_url(
            width=600,
            crop="scale",
            quality="auto:good", fetch_format="auto",
        )


class ProductVariant(models.Model):
    product      = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    label        = models.CharField(max_length=100)
    extra_price  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock        = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name    = "Variante"
        unique_together = [["product", "label"]]
        ordering        = ["label"]

    def __str__(self):
        return f"{self.product.name} — {self.label}"
