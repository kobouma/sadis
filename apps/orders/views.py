from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.orders.models import Cart, CartItem, Order
from apps.orders.serializers import CartItemSerializer, CartSerializer, OrderSerializer
from core.utils.response import success, created, error

class CartView(APIView):
    permission_classes = [IsAuthenticated]
    def _cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart
    def get(self, request):
        return success(data=CartSerializer(self._cart(request.user)).data)
    def delete(self, request):
        self._cart(request.user).items.all().delete()
        return success(message="Panier vidé.")

class CartItemView(APIView):
    permission_classes = [IsAuthenticated]
    def _cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart
    def post(self, request):
        cart = self._cart(request.user)
        s = CartItemSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save(cart=cart)
        return created(data=CartSerializer(cart).data, message="Article ajouté.")
    def patch(self, request, item_id):
        cart = self._cart(request.user)
        try: item = cart.items.get(pk=item_id)
        except CartItem.DoesNotExist:
            return error("Article introuvable.", status_code=status.HTTP_404_NOT_FOUND)
        qty = request.data.get("quantity")
        if not qty or int(qty) < 1:
            return error("La quantité doit être ≥ 1.")
        item.quantity = int(qty); item.save()
        return success(data=CartSerializer(cart).data, message="Quantité mise à jour.")
    def delete(self, request, item_id):
        cart = self._cart(request.user)
        try: cart.items.get(pk=item_id).delete()
        except CartItem.DoesNotExist:
            return error("Article introuvable.", status_code=status.HTTP_404_NOT_FOUND)
        return success(data=CartSerializer(cart).data, message="Article retiré.")

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if user.is_seller:
            return Order.objects.filter(shop__owner=user).select_related("buyer","shop").prefetch_related("items")
        return Order.objects.filter(buyer=user).select_related("buyer","shop").prefetch_related("items")
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        s  = request.query_params.get("status")
        if s: qs = qs.filter(status=s)
        return success(data=self.get_serializer(qs, many=True).data)
    def retrieve(self, request, *args, **kwargs):
        return success(data=self.get_serializer(self.get_object()).data)