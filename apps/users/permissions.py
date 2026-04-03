from rest_framework.permissions import BasePermission
from .models import Role

class IsSeller(BasePermission):
    message = "Seuls les vendeurs peuvent effectuer cette action."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.SELLER

class IsDeliveryAgent(BasePermission):
    message = "Seuls les livreurs peuvent effectuer cette action."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.DELIVERY

class IsPhoneVerified(BasePermission):
    message = "Votre numéro doit être vérifié."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.phone_verified

class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff