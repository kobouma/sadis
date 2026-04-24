# apps/products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from apps.products.models import Category, Product, ProductImage, ProductVariant


class ProductImageInline(TabularInline):
    model           = ProductImage
    extra           = 0
    fields          = ["image_preview", "file", "media_type", "order", "is_cover"]
    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="border-radius:6px;object-fit:cover;"/>',
                obj.url
            )
        return "—"
    image_preview.short_description = "Aperçu"


class ProductVariantInline(TabularInline):
    model  = ProductVariant
    extra  = 0
    fields = ["label", "extra_price", "stock", "is_available"]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display        = ["name", "slug", "icon", "parent"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    inlines         = [ProductImageInline, ProductVariantInline]
    list_display    = ["cover_preview", "name", "shop", "price_display",
                       "stock", "is_available", "views_count", "sales_count"]
    list_filter     = ["is_available", "category", "shop"]
    search_fields   = ["name", "shop__name"]
    readonly_fields = ["id", "slug", "views_count", "sales_count", "created_at"]
    list_editable   = ["is_available", "stock"]
    list_per_page   = 20
    actions         = ["make_available", "make_unavailable"]

    fieldsets = (
        ("Informations", {"fields": ("id", "slug", "name", "description", "shop", "category")}),
        ("Prix & Stock", {"fields": ("price", "old_price", "stock", "is_available")}),
        ("Stats",        {"fields": ("views_count", "sales_count", "created_at")}),
    )

    def cover_preview(self, obj):
        cover = obj.images.filter(is_cover=True).first() or obj.images.first()
        if cover:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="border-radius:6px;object-fit:cover;"/>',
                cover.url
            )
        return "—"
    cover_preview.short_description = "Photo"

    def price_display(self, obj):
        if obj.old_price:
            return format_html(
                '<span style="color:#C62828;font-weight:600">{} XOF</span> '
                '<span style="color:#9E9E9E;text-decoration:line-through;font-size:11px">{}</span>',
                f"{obj.price:,.0f}", f"{obj.old_price:,.0f}"
            )
        return format_html('<span style="font-weight:600">{} XOF</span>', f"{obj.price:,.0f}")
    price_display.short_description = "Prix"

    @admin.action(description="✅ Rendre disponibles")
    def make_available(self, request, queryset):
        count = queryset.update(is_available=True)
        self.message_user(request, f"{count} produit(s) disponible(s).")

    @admin.action(description="🚫 Rendre indisponibles")
    def make_unavailable(self, request, queryset):
        count = queryset.update(is_available=False)
        self.message_user(request, f"{count} produit(s) indisponible(s).")