# apps/chat/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from apps.chat.models import Conversation, Message


class MessageInline(TabularInline):
    model           = Message
    extra           = 0
    max_num         = 20
    readonly_fields = ["id", "sender", "msg_type", "payload", "is_read", "created_at"]


@admin.register(Conversation)
class ConversationAdmin(ModelAdmin):
    inlines         = [MessageInline]
    list_display    = ["id", "buyer", "seller", "product", "status", "escrow_amount"]
    list_filter     = ["status"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display    = ["id", "conversation", "sender", "msg_type", "is_read", "created_at"]
    list_filter     = ["msg_type", "is_read"]
    readonly_fields = ["id", "created_at"]