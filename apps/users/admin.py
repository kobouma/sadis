# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, StackedInline
from .models import User, Profile, DeliveryAgent


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
    list_display    = ["phone", "full_name", "is_delivery",
                       "phone_verified", "is_active", "date_joined"]
    list_filter     = ["is_delivery", "phone_verified", "is_active"]
    search_fields   = ["phone", "full_name"]
    ordering        = ["-date_joined"]
    readonly_fields = ["id", "date_joined"]
    list_per_page   = 25
    actions         = ["activate_users", "deactivate_users", "verify_phones"]

    fieldsets = (
        (None,           {"fields": ("id", "phone", "password")}),
        ("Informations", {"fields": ("full_name", "email", "phone_verified")}),
        ("Livraison",    {"fields": ("is_delivery",)}),
        ("Permissions",  {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Dates",        {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields":  ("phone", "full_name", "password1", "password2")}),
    )

    @admin.action(description="✅ Activer les comptes")
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} compte(s) activé(s).")

    @admin.action(description="🚫 Désactiver les comptes")
    def deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} compte(s) désactivé(s).")

    @admin.action(description="📱 Vérifier les téléphones")
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


@admin.register(DeliveryAgent)
class DeliveryAgentAdmin(ModelAdmin):
    list_display  = ["user", "city", "vehicle_type", "status",
                     "rating", "total_deliveries", "is_online"]
    list_filter   = ["status", "vehicle_type", "city"]
    search_fields = ["user__phone", "user__full_name", "city"]
    list_editable = ["status", "is_online"]
    readonly_fields = ["created_at", "updated_at"]
    actions       = ["activate_agents", "deactivate_agents"]

    @admin.action(description="✅ Activer les livreurs")
    def activate_agents(self, request, queryset):
        for agent in queryset:
            agent.activate()
        self.message_user(request, f"{queryset.count()} livreur(s) activé(s).")

    @admin.action(description="🚫 Désactiver les livreurs")
    def deactivate_agents(self, request, queryset):
        queryset.update(status="inactive")
        queryset.update(user__is_delivery=False)