from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from core.utils.mixins import ApiResponseMixin
from core.utils.response import success, error
from core.permissions.permissions import IsShopOwner
from apps.users.permissions import IsSeller
from .models import Shop, ShopCategory
from .serializers import ShopSerializer, ShopCreateUpdateSerializer, ShopCategorySerializer


class ShopCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = ShopCategory.objects.all()
    serializer_class   = ShopCategorySerializer
    permission_classes = [AllowAny]


class ShopViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    lookup_field    = "slug"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields   = ["name", "description", "city"]
    ordering        = ["-created_at"]

    def get_queryset(self):
        return Shop.objects.filter(is_active=True).select_related("owner", "category")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ShopCreateUpdateSerializer
        return ShopSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsSeller()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsShopOwner()]
        return [IsAuthenticatedOrReadOnly()]

    # ── GET  /shops/mine/ → boutique du vendeur ───────────────
    # ── POST /shops/mine/ → créer une boutique ────────────────
    # ── PATCH/shops/mine/ → modifier la boutique ─────────────
    @action(detail=False, methods=["get", "post", "patch"],
            permission_classes=[IsAuthenticated, IsSeller])
    def mine(self, request):

        if request.method == "GET":
            shop = Shop.objects.filter(owner=request.user).first()
            return success(data=ShopSerializer(shop).data if shop else None)

        if request.method == "POST":
            if Shop.objects.filter(owner=request.user).exists():
                return error(message="Vous avez déjà une boutique.", status_code=400)
            serializer = ShopCreateUpdateSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                shop = serializer.save(owner=request.user)
                return success(data=ShopSerializer(shop).data, status_code=201)
            return error(message="Données invalides.", details=serializer.errors, status_code=400)

        if request.method == "PATCH":
            shop = Shop.objects.filter(owner=request.user).first()
            if not shop:
                return error(message="Aucune boutique trouvée.", status_code=404)
            serializer = ShopCreateUpdateSerializer(
                shop, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                shop = serializer.save()
                return success(data=ShopSerializer(shop).data)
            return error(message="Données invalides.", details=serializer.errors, status_code=400)