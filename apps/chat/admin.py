from django.contrib import admin

from apps.chat.models import Conversation, Message

class MessageInline(admin.TabularInline):
    model           = Message; extra = 0; max_num = 20
    readonly_fields = ["id", "sender", "msg_type", "payload", "is_read", "created_at"]

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    inlines       = [MessageInline]
    list_display  = ["id", "buyer", "seller", "product", "status", "escrow_amount"]
    list_filter   = ["status"]
    readonly_fields = ["id", "created_at", "updated_at"]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ["id", "conversation", "sender", "msg_type", "is_read", "created_at"]
    list_filter   = ["msg_type", "is_read"]
    readonly_fields = ["id", "created_at"]