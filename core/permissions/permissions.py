from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsShopOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        shop = getattr(obj, "shop", obj)
        return shop.owner == request.user

class IsShopOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS: return True
        return getattr(obj, "shop", obj).owner == request.user

class IsParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in (obj.buyer, obj.seller)

class IsDeliveryAgent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "delivery"

class IsVerified(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.phone_verified

