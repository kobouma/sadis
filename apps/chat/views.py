from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.chat.models import Conversation, Message
from apps.chat.serializers import ConversationCreateSerializer, ConversationSerializer
from core.utils.response import success, created

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names  = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        return (Conversation.objects.filter(buyer=user) |
                Conversation.objects.filter(seller=user)).distinct()\
               .select_related("buyer","seller","product").prefetch_related("messages")

    def get_serializer_class(self):
        return ConversationCreateSerializer if self.action == "create" else ConversationSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().order_by("-updated_at")
        return success(data=self.get_serializer(qs, many=True, context={"request": request}).data)

    def create(self, request, *args, **kwargs):
        s = ConversationCreateSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        return created(data=ConversationSerializer(s.save(), context={"request": request}).data,
                       message="Conversation ouverte.")

    def retrieve(self, request, *args, **kwargs):
        conv = self.get_object()
        return success(data={
            "conversation": ConversationSerializer(conv, context={"request": request}).data,
            "messages":     MessageSerializer(conv.messages.order_by("created_at"), many=True).data,
        })

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        updated = Message.objects.filter(conversation=self.get_object(), is_read=False)\
                         .exclude(sender=request.user).update(is_read=True)
        return success(message=f"{updated} message(s) lu(s).")