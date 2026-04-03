from django.contrib import admin
from .models import Shop, ShopCategory

@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display        = ["name", "slug", "icon"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display    = ["name", "owner", "category", "city", "is_active", "is_verified"]
    list_filter     = ["is_active", "is_verified", "category"]
    search_fields   = ["name", "owner__phone", "city"]
    readonly_fields = ["id", "slug", "created_at", "updated_at"]
    list_editable   = ["is_active", "is_verified"]