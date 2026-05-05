# apps/shops/views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from core.utils.mixins import ApiResponseMixin
from core.utils.response import success, error
from core.permissions.permissions import IsShopOwner
from .models import Shop, ShopCategory, ShopFollow
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
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsShopOwner()]
        return [IsAuthenticatedOrReadOnly()]

    # ── GET  /shops/mine/ → boutique du vendeur ───────────────
    # ── POST /shops/mine/ → créer une boutique ────────────────
    # ── PATCH/shops/mine/ → modifier la boutique ─────────────
    @action(
        detail=False,
        methods=["get", "post", "patch"],
        # ← Fix : IsAuthenticated uniquement — pas IsSeller
        # Tout utilisateur connecté peut créer sa boutique
        permission_classes=[IsAuthenticated],
    )
    def mine(self, request):

        if request.method == "GET":
            shop = Shop.objects.filter(owner=request.user).first()
            return success(data=ShopSerializer(shop).data if shop else None)

        if request.method == "POST":
            if Shop.objects.filter(owner=request.user).exists():
                # Boutique déjà existante → retourner la boutique existante
                shop = Shop.objects.filter(owner=request.user).first()
                return success(data=ShopSerializer(shop).data)

            serializer = ShopCreateUpdateSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                shop = serializer.save(owner=request.user)
                return success(data=ShopSerializer(shop).data, status_code=201)
            return error(
                message="Données invalides.",
                details=serializer.errors,
                status_code=400,
            )

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
            return error(
                message="Données invalides.",
                details=serializer.errors,
                status_code=400,
            )

    # ── GET /shops/followed/ → boutiques suivies par l'utilisateur ──
    @action(
        detail=False,
        methods=["get"],
        url_path="followed",
        permission_classes=[IsAuthenticated],
    )
    def followed(self, request):
        shop_ids = ShopFollow.objects.filter(
            user=request.user
        ).values_list("shop_id", flat=True)
        shops = Shop.objects.filter(
            id__in=shop_ids, is_active=True
        ).select_related("owner", "category")
        return success(
            data=ShopSerializer(shops, many=True, context={"request": request}).data
        )

    # ── POST /shops/{slug}/follow/ → toggle abonnement ───────
    @action(
        detail=True,
        methods=["post"],
        url_path="follow",
        permission_classes=[IsAuthenticated],
    )
    def follow(self, request, slug=None):
        shop = self.get_object()
        follow_obj, is_new = ShopFollow.objects.get_or_create(
            user=request.user, shop=shop)
        total = ShopFollow.objects.filter(shop=shop).count()
        if not is_new:
            follow_obj.delete()
            return success(
                data={"following": False, "followers_count": max(0, total - 1)},
                message="Boutique désabonnée.")
        return success(
            data={"following": True, "followers_count": total},
            message="Boutique suivie.")