from rest_framework import serializers

from apps.chat.models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    sender_id   = serializers.UUIDField(source="sender.id",        read_only=True)
    class Meta:
        model  = Message
        fields = ["id", "msg_type", "payload", "sender_name", "sender_id", "is_read", "created_at"]
        read_only_fields = ["id", "sender_name", "sender_id", "is_read", "created_at"]

class ConversationSerializer(serializers.ModelSerializer):
    buyer_name   = serializers.CharField(source="buyer.full_name",  read_only=True)
    seller_name  = serializers.CharField(source="seller.full_name", read_only=True)
    product_name = serializers.CharField(source="product.name",     read_only=True, default=None)
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
        user = self.context["request"].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()

class ConversationCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    class Meta:
        model  = Conversation
        fields = ["seller", "product_id"]
    def validate(self, data):
        buyer  = self.context["request"].user
        seller = data["seller"]
        if buyer == seller:
            raise serializers.ValidationError("Vous ne pouvez pas vous écrire à vous-même.")
        product = None
        pid = data.get("product_id")
        if pid:
            from apps.products.models import Product
            try: product = Product.objects.get(pk=pid)
            except Product.DoesNotExist:
                raise serializers.ValidationError("Produit introuvable.")
        conv, _ = Conversation.objects.get_or_create(buyer=buyer, seller=seller, product=product)
        data["conversation"] = conv
        return data
    def create(self, validated_data):
        return validated_data["conversation"]