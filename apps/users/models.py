# apps/users/models.py
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from cloudinary.models import CloudinaryField


# ── Plus de rôle seller/buyer — tout utilisateur peut vendre ──
# Seul le rôle delivery reste pour les livreurs professionnels

class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Le numéro de téléphone est obligatoire.")
        extra_fields.setdefault("is_active", True)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault("is_staff",       True)
        extra_fields.setdefault("is_superuser",   True)
        extra_fields.setdefault("is_delivery",    False)
        extra_fields.setdefault("phone_verified", True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone          = models.CharField(max_length=20, unique=True, verbose_name="Téléphone")
    full_name      = models.CharField(max_length=150, verbose_name="Nom complet")
    email          = models.EmailField(blank=True, default="", verbose_name="Email")

    # ── Livraison — flag dédié (pas un rôle) ──────────────────
    # True = livreur professionnel inscrit sur la plateforme
    is_delivery    = models.BooleanField(default=False, verbose_name="Est livreur")

    phone_verified = models.BooleanField(default=False)
    is_active      = models.BooleanField(default=True)
    is_staff       = models.BooleanField(default=False)
    date_joined    = models.DateTimeField(default=timezone.now)

    # ── OAuth Social ──────────────────────────────────────────
    social_provider = models.CharField(max_length=20, blank=True, default="")
    social_id       = models.CharField(max_length=255, blank=True, default="")

    objects = UserManager()

    USERNAME_FIELD  = "phone"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name        = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering            = ["-date_joined"]

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    # ── Propriétés C2C ────────────────────────────────────────
    @property
    def is_seller(self):
        """Tout utilisateur avec au moins une boutique active est vendeur."""
        return self.shops.filter(is_active=True).exists()

    @property
    def has_shop(self):
        return self.shops.exists()

    @property
    def is_buyer(self):
        """Tout utilisateur peut acheter — toujours True."""
        return True


class Profile(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar  = CloudinaryField("avatar", folder="sadis/avatars", blank=True, null=True)
    city    = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    bio     = models.TextField(blank=True)

    class Meta:
        verbose_name = "Profil"

    def __str__(self):
        return f"Profil de {self.user.full_name}"


# ── Modèle livreur professionnel ──────────────────────────────
class DeliveryAgent(models.Model):
    """
    Profil étendu pour les livreurs professionnels.
    Un User devient livreur en créant un DeliveryAgent + is_delivery=True.
    """

    class VehicleType(models.TextChoices):
        MOTO    = "moto",    "Moto"
        VELO    = "velo",    "Vélo"
        VOITURE = "voiture", "Voiture"
        AUTRE   = "autre",   "Autre"

    class Status(models.TextChoices):
        PENDING  = "pending",  "En attente de validation"
        ACTIVE   = "active",   "Actif"
        INACTIVE = "inactive", "Inactif"
        BANNED   = "banned",   "Suspendu"

    user         = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="delivery_agent"
    )
    vehicle_type = models.CharField(
        max_length=20, choices=VehicleType.choices, default=VehicleType.MOTO
    )
    vehicle_plate = models.CharField(max_length=20, blank=True)
    city          = models.CharField(max_length=100)
    status        = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    id_document   = CloudinaryField(
        "document", folder="sadis/agents/docs", blank=True, null=True
    )
    rating        = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    total_deliveries = models.PositiveIntegerField(default=0)
    is_online     = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Livreur"
        verbose_name_plural = "Livreurs"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"Livreur {self.user.full_name} — {self.city}"

    def activate(self):
        self.status = self.Status.ACTIVE
        self.user.is_delivery = True
        self.user.save(update_fields=["is_delivery"])
        self.save(update_fields=["status"])


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)