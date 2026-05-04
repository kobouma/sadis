# apps/products/serializers.py
from rest_framework import serializers
from apps.products.models import Category, Product, ProductImage, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ["id", "name", "slug", "icon", "parent"]


class ProductImageSerializer(serializers.ModelSerializer):
    url       = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    card_url  = serializers.SerializerMethodField()

    class Meta:
        model  = ProductImage
        fields = ["id", "url", "thumbnail", "card_url",
                  "media_type", "order", "is_cover"]

    def get_url(self, obj):       return obj.url
    def get_thumbnail(self, obj): return obj.thumbnail_url
    def get_card_url(self, obj):  return obj.card_url


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductVariant
        fields = ["id", "label", "extra_price", "stock", "is_available"]


class ProductListSerializer(serializers.ModelSerializer):
    cover_image      = serializers.SerializerMethodField()
    shop_name        = serializers.CharField(source="shop.name", read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Product
        fields = ["id", "name", "slug", "price", "old_price",
                  "discount_percent", "cover_image", "shop_name", "sales_count"]

    def get_cover_image(self, obj):
        cover = obj.images.filter(is_cover=True).first() or obj.images.first()
        return cover.card_url if cover else None


class ProductSerializer(serializers.ModelSerializer):
    images           = ProductImageSerializer(many=True, read_only=True)
    variants         = ProductVariantSerializer(many=True, read_only=True)
    category         = CategorySerializer(read_only=True)
    shop_name        = serializers.CharField(source="shop.name",     read_only=True)
    shop_slug        = serializers.CharField(source="shop.slug",     read_only=True)
    shop_owner_id    = serializers.CharField(source="shop.owner.id", read_only=True)
    shop_logo        = serializers.SerializerMethodField()
    shop             = serializers.SerializerMethodField()
    discount_percent = serializers.IntegerField(read_only=True)
    reviews          = serializers.SerializerMethodField()
    review_count     = serializers.SerializerMethodField()
    rating           = serializers.SerializerMethodField()
    is_liked         = serializers.SerializerMethodField()
    likes_count      = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = ["id", "name", "slug", "description",
                  "price", "old_price", "discount_percent",
                  "stock", "is_available", "views_count", "sales_count",
                  "shop_name", "shop_slug", "shop_owner_id", "shop_logo",
                  "shop", "category", "images", "variants",
                  "reviews", "review_count", "rating",
                  "is_liked", "likes_count",
                  "created_at"]

    def get_shop_logo(self, obj):
        return obj.shop.logo.url if obj.shop.logo else None

    def get_shop(self, obj):
        request = self.context.get("request")
        is_following = False
        if request and request.user.is_authenticated:
            from apps.shops.models import ShopFollow
            is_following = ShopFollow.objects.filter(
                user=request.user, shop=obj.shop).exists()
        return {
            "id":           str(obj.shop.id),
            "name":         obj.shop.name,
            "slug":         obj.shop.slug,
            "logo":         obj.shop.logo.url if obj.shop.logo else None,
            "city":         obj.shop.city,
            "is_verified":  obj.shop.is_verified,
            "owner_id":     str(obj.shop.owner_id),
            "is_following": is_following,
        }

    def get_reviews(self, obj):
        from apps.reviews.serializers import ReviewSerializer
        qs = obj.reviews.select_related("user").prefetch_related("images")[:20]
        return ReviewSerializer(qs, many=True, context=self.context).data

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_rating(self, obj):
        from django.db.models import Avg
        avg = obj.reviews.aggregate(avg=Avg("rating"))["avg"]
        return round(float(avg), 1) if avg else 0.0

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_likes_count(self, obj):
        return obj.likes.count()


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    # ← Retourner slug et id après création pour que Flutter puisse uploader les images
    slug = serializers.SlugField(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category",
        required=False, allow_null=True)

    class Meta:
        model  = Product
        fields = ["id", "slug", "name", "description", "price", "old_price",
                  "stock", "is_available", "category_id"]
        read_only_fields = ["id", "slug"]