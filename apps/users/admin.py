# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, StackedInline
from .models import User, Profile


class ProfileInline(StackedInline):
    model           = Profile
    extra           = 0
    fields          = ["avatar_preview", "avatar", "city", "address", "bio"]
    readonly_fields = ["avatar_preview"]

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="border-radius:50%;object-fit:cover;"/>',
                obj.avatar.url
            )
        return "—"
    avatar_preview.short_description = "Aperçu"


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    inlines         = [ProfileInline]
    list_display    = ["phone", "full_name", "role_badge",
                       "phone_verified", "is_active", "date_joined"]
    list_filter     = ["role", "phone_verified", "is_active"]
    search_fields   = ["phone", "full_name"]
    ordering        = ["-date_joined"]
    readonly_fields = ["id", "date_joined"]
    list_per_page   = 25
    actions         = ["activate_users", "deactivate_users", "verify_phones"]

    fieldsets = (
        (None,           {"fields": ("id", "phone", "password")}),
        ("Informations", {"fields": ("full_name", "role", "phone_verified")}),
        ("Permissions",  {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Dates",        {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields":  ("phone", "full_name", "role", "password1", "password2")}),
    )

    def role_badge(self, obj):
        colors = {
            "buyer":    ("#E8F5E9", "#2E7D32"),
            "seller":   ("#E3F2FD", "#1565C0"),
            "delivery": ("#FFF3E0", "#E65100"),
        }
        bg, fg = colors.get(obj.role, ("#F5F5F5", "#616161"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;'
            'border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            bg, fg, obj.get_role_display()
        )
    role_badge.short_description = "Rôle"

    @admin.action(description="✅ Activer les comptes sélectionnés")
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} compte(s) activé(s).")

    @admin.action(description="🚫 Désactiver les comptes sélectionnés")
    def deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} compte(s) désactivé(s).")

    @admin.action(description="📱 Marquer téléphones comme vérifiés")
    def verify_phones(self, request, queryset):
        count = queryset.update(phone_verified=True)
        self.message_user(request, f"{count} téléphone(s) vérifié(s).")


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display    = ["user", "city", "avatar_preview"]
    search_fields   = ["user__phone", "user__full_name"]
    readonly_fields = ["avatar_preview"]

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" '
                'style="border-radius:50%;object-fit:cover;"/>',
                obj.avatar.url
            )
        return "—"
    avatar_preview.short_description = "Avatar"