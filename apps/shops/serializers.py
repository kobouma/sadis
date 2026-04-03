from rest_framework import serializers
from .models import Shop, ShopCategory


class ShopCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = ShopCategory
        fields = ["id", "name", "slug", "icon"]


class ShopSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)
    category   = ShopCategorySerializer(read_only=True)
    # URLs CDN Cloudinary pour logo et banner
    logo   = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()

    class Meta:
        model  = Shop
        fields = ["id", "name", "slug", "description", "logo", "banner",
                  "phone", "city", "address", "latitude", "longitude",
                  "is_active", "is_verified", "owner_name", "category", "created_at"]
        read_only_fields = ["id", "slug", "is_verified", "created_at", "owner_name"]

    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None

    def get_banner(self, obj):
        return obj.banner.url if obj.banner else None


class ShopCreateUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ShopCategory.objects.all(), source="category",
        required=False, allow_null=True)

    class Meta:
        model  = Shop
        fields = ["name", "description", "logo", "banner",
                  "phone", "city", "address", "latitude", "longitude",
                  "is_active", "category_id"]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)
