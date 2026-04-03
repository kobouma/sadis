import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Role(models.TextChoices):
    BUYER    = "buyer",    "Acheteur"
    SELLER   = "seller",   "Vendeur"
    DELIVERY = "delivery", "Livreur"


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
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.BUYER)
        extra_fields.setdefault("phone_verified", True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone          = models.CharField(max_length=20, unique=True, verbose_name="Téléphone")
    full_name      = models.CharField(max_length=150, verbose_name="Nom complet")
    role           = models.CharField(max_length=20, choices=Role.choices,
                                      default=Role.BUYER, db_index=True)
    phone_verified = models.BooleanField(default=False)
    is_active      = models.BooleanField(default=True)
    is_staff       = models.BooleanField(default=False)
    date_joined    = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD  = "phone"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name        = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering            = ["-date_joined"]

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    @property
    def is_buyer(self):    return self.role == Role.BUYER
    @property
    def is_seller(self):   return self.role == Role.SELLER
    @property
    def is_delivery(self): return self.role == Role.DELIVERY


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # ── Cloudinary : remplace ImageField ─────────────────────
    avatar = CloudinaryField("avatar", folder="sadis/avatars",
                             blank=True, null=True)

    city    = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    bio     = models.TextField(blank=True)

    class Meta:
        verbose_name = "Profil"

    def __str__(self):
        return f"Profil de {self.user.full_name}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
