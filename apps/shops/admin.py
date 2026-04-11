# apps/shops/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Shop, ShopCategory


@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display        = ["name", "slug", "icon"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display    = ["logo_preview", "name", "owner", "category",
                       "city", "is_active", "is_verified", "created_at"]
    list_filter     = ["is_active", "is_verified", "category"]
    search_fields   = ["name", "owner__phone", "city"]
    readonly_fields = ["id", "slug", "logo_preview", "banner_preview", "created_at", "updated_at"]
    list_editable   = ["is_active", "is_verified"]
    list_per_page   = 20
    actions         = ["verify_shops", "activate_shops", "deactivate_shops"]

    fieldsets = (
        ("Informations",  {"fields": ("id", "slug", "name", "description", "owner", "category")}),
        ("Médias",        {"fields": ("logo_preview", "logo", "banner_preview", "banner")}),
        ("Contact",       {"fields": ("phone", "city", "address", "latitude", "longitude")}),
        ("Statut",        {"fields": ("is_active", "is_verified")}),
        ("Dates",         {"fields": ("created_at", "updated_at")}),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="40" height="40" '
                'style="border-radius:8px;object-fit:cover;"/>',
                obj.logo.url
            )
        return "—"
    logo_preview.short_description = "Logo"

    def banner_preview(self, obj):
        if obj.banner:
            return format_html(
                '<img src="{}" width="200" height="60" '
                'style="border-radius:8px;object-fit:cover;"/>',
                obj.banner.url
            )
        return "—"
    banner_preview.short_description = "Bannière"

    def status_badges(self, obj):
        badges = []
        if obj.is_active:
            badges.append('<span style="background:#E8F5E9;color:#2E7D32;'
                         'padding:2px 6px;border-radius:10px;font-size:11px">Actif</span>')
        else:
            badges.append('<span style="background:#FFEBEE;color:#C62828;'
                         'padding:2px 6px;border-radius:10px;font-size:11px">Inactif</span>')
        if obj.is_verified:
            badges.append('<span style="background:#E3F2FD;color:#1565C0;'
                         'padding:2px 6px;border-radius:10px;font-size:11px">✓ Vérifié</span>')
        return format_html(" ".join(badges))
    status_badges.short_description = "Statut"

    @admin.action(description="✅ Vérifier les boutiques sélectionnées")
    def verify_shops(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f"{count} boutique(s) vérifiée(s).")

    @admin.action(description="🟢 Activer")
    def activate_shops(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} boutique(s) activée(s).")

    @admin.action(description="🔴 Désactiver")
    def deactivate_shops(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} boutique(s) désactivée(s).")