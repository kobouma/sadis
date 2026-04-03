from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

class ProfileInline(admin.StackedInline):
    model  = Profile
    extra  = 0
    fields = ["avatar", "city", "address", "bio"]

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines         = [ProfileInline]
    list_display    = ["phone", "full_name", "role", "phone_verified", "is_active"]
    list_filter     = ["role", "phone_verified", "is_active"]
    search_fields   = ["phone", "full_name"]
    ordering        = ["-date_joined"]
    readonly_fields = ["id", "date_joined"]
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

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ["user", "city"]
    search_fields = ["user__phone", "user__full_name"]