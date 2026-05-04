import cloudinary.uploader
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from apps.products.filters import ProductFilter
from apps.products.models import Category, Product, ProductImage
from apps.products.serializers import (
    CategorySerializer, ProductCreateUpdateSerializer,
    ProductImageSerializer, ProductListSerializer, ProductSerializer,
)
from core.utils.mixins import ApiResponseMixin
from core.utils.response import success, created, error
from core.permissions.permissions import IsShopOwner
from apps.users.permissions import HasShop as IsSeller


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = Category.objects.filter(parent=None)
    serializer_class   = CategorySerializer
    permission_classes = [AllowAny]


class ProductViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    lookup_field    = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields   = ["name", "description", "shop__name"]
    ordering_fields = ["price", "created_at", "sales_count"]
    ordering        = ["-created_at"]

    def get_queryset(self):
        return (Product.objects.filter(is_available=True)
                .select_related("shop", "shop__owner", "category")
                .prefetch_related("images", "variants", "reviews__user", "likes"))

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsShopOwner()]
        return [IsAuthenticatedOrReadOnly()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Product.objects.filter(pk=instance.pk).update(
            views_count=instance.views_count + 1
        )
        return success(data=ProductSerializer(instance, context={"request": request}).data)

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError
        shop_slug = self.request.query_params.get("shop", "").strip()
        if not shop_slug:
            raise ValidationError("Paramètre 'shop' manquant.")
        shop = self.request.user.shops.filter(slug=shop_slug).first()
        if not shop:
            raise ValidationError("Boutique introuvable ou vous n'en êtes pas propriétaire.")
        serializer.save(shop=shop)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny], url_path="flash-sale")
    def flash_sale(self, request):
        qs = self.get_queryset().filter(old_price__isnull=False)
        return success(data=ProductListSerializer(qs, many=True, context={"request": request}).data)

    # ── Upload image(s) vers Cloudinary ──────────────────────
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsShopOwner],
        parser_classes=[MultiPartParser, FormParser],
        url_path="images",
    )
    def add_image(self, request, slug=None):
        """
        Upload une ou plusieurs images pour un produit.
        Form-data : images[] (fichiers)
        """
        product = self.get_object()
        files   = request.FILES.getlist("images") or (
            [request.FILES["file"]] if "file" in request.FILES else []
        )

        if not files:
            return error("Aucune image fournie.", status_code=status.HTTP_400_BAD_REQUEST)

        uploaded = []
        errors   = []

        for i, file in enumerate(files):
            try:
                result = cloudinary.uploader.upload(
                    file,
                    folder=f"sadis/products/{product.slug}",
                    transformation=[
                        {"quality": "auto:good", "fetch_format": "auto"},
                    ],
                    eager=[
                        {"width": 400, "height": 400, "crop": "fill", "gravity": "auto"},
                        {"width": 600, "crop": "scale"},
                    ],
                    eager_async=False,
                )
                # Détecter automatiquement photo vs vidéo
                resource_type = result.get("resource_type", "image")
                media_type = (
                    ProductImage.MediaType.VIDEO
                    if resource_type == "video"
                    else ProductImage.MediaType.PHOTO
                )
                img = ProductImage.objects.create(
                    product    = product,
                    file       = result["public_id"],
                    media_type = media_type,
                    order      = product.images.count(),
                    is_cover   = not product.images.exists(),  # 1ère image = cover
                )
                uploaded.append(ProductImageSerializer(img).data)

            except Exception as e:
                errors.append({"file": file.name, "error": str(e)})

        return created(
            data={"uploaded": uploaded, "errors": errors, "count": len(uploaded)},
            message=f"{len(uploaded)} image(s) uploadée(s).",
        )

    # ── Suppression image + nettoyage Cloudinary ─────────────
    @action(
        detail=True,
        methods=["delete"],
        permission_classes=[IsAuthenticated, IsShopOwner],
        url_path=r"images/(?P<image_id>\d+)",
    )
    def delete_image(self, request, slug=None, image_id=None):
        try:
            img = self.get_object().images.get(pk=image_id)
        except ProductImage.DoesNotExist:
            return error("Média introuvable.", status_code=status.HTTP_404_NOT_FOUND)

        # Supprimer de Cloudinary avant de supprimer de la BDD
        if img.file:
            try:
                cloudinary.uploader.destroy(
                    str(img.file),
                    resource_type="video" if img.media_type == "video" else "image",
                )
            except Exception:
                pass  # Ne pas bloquer si Cloudinary échoue

        img.delete()
        return success(message="Média supprimé.")

    # ── GET /products/liked/ → produits likés par l'utilisateur ──
    @action(
        detail=False,
        methods=["get"],
        url_path="liked",
        permission_classes=[IsAuthenticated],
    )
    def liked(self, request):
        from apps.reviews.models import Like
        liked_ids = Like.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)
        qs = Product.objects.filter(
            id__in=liked_ids, is_available=True
        ).select_related("shop", "shop__category")
        serializer = ProductListSerializer(
            qs, many=True, context={"request": request}
        )
        return success(data=serializer.data)