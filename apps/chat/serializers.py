# apps/chat/serializers.py
from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    sender_id   = serializers.UUIDField(source="sender.id",        read_only=True)

    class Meta:
        model  = Message
        fields = ["id", "msg_type", "payload", "sender_name",
                  "sender_id", "is_read", "created_at"]
        read_only_fields = ["id", "sender_name", "sender_id",
                            "is_read", "created_at"]

    def create(self, validated_data):
        # Injecter conversation et sender depuis le contexte
        request = self.context.get('request')
        conv    = self.context.get('conversation')
        if conv:
            validated_data['conversation'] = conv
        if request:
            validated_data['sender'] = request.user
        return super().create(validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    buyer_name   = serializers.CharField(source="buyer.full_name",  read_only=True)
    seller_name  = serializers.CharField(source="seller.full_name", read_only=True)
    product_name = serializers.CharField(source="product.name",
                                         read_only=True, default=None)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model  = Conversation
        fields = ["id", "status", "escrow_amount",
                  "buyer_name", "seller_name", "product_name",
                  "last_message", "unread_count", "created_at", "updated_at"]

    def get_last_message(self, obj):
        msg = obj.messages.last()
        return MessageSerializer(msg).data if msg else None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        return obj.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()