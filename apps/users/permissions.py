# apps/users/permissions.py
from rest_framework.permissions import BasePermission


class IsDeliveryAgent(BasePermission):
    """Livreur professionnel validé."""
    message = "Seuls les livreurs peuvent effectuer cette action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_delivery
            and hasattr(request.user, "delivery_agent")
            and request.user.delivery_agent.status == "active"
        )


class HasShop(BasePermission):
    """L'utilisateur a au moins une boutique active — remplace IsSeller."""
    message = "Créez une boutique pour effectuer cette action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.shops.filter(is_active=True).exists()
        )


class IsShopOwner(BasePermission):
    """L'objet appartient à la boutique de l'utilisateur."""
    def has_object_permission(self, request, view, obj):
        shop = getattr(obj, "shop", None)
        if shop:
            return shop.owner == request.user
        return False


class IsPhoneVerified(BasePermission):
    message = "Votre numéro doit être vérifié."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.phone_verified


class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


# ── Alias pour rétrocompatibilité ─────────────────────────────
IsSeller = HasShop