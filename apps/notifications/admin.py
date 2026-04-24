# apps/notifications/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display    = ["title", "recipient", "notif_type", "is_read", "created_at"]
    list_filter     = ["notif_type", "is_read"]
    search_fields   = ["recipient__phone", "title"]
    readonly_fields = ["id", "created_at"]