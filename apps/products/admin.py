from django.contrib import admin

from apps.products.models import Category, Product, ProductImage, ProductVariant

class ProductImageInline(admin.TabularInline):
    model  = ProductImage; extra = 0
    fields = ["file", "media_type", "order", "is_cover"]

class ProductVariantInline(admin.TabularInline):
    model  = ProductVariant; extra = 0
    fields = ["label", "extra_price", "stock", "is_available"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ["name", "slug", "icon", "parent"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines         = [ProductImageInline, ProductVariantInline]
    list_display    = ["name", "shop", "price", "stock", "is_available"]
    list_filter     = ["is_available", "category"]
    search_fields   = ["name", "shop__name"]
    readonly_fields = ["id", "slug", "views_count", "sales_count", "created_at"]
    list_editable   = ["is_available", "stock"]
