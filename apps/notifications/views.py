from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers as drf_serializers
from core.utils.response import success
from .models import Notification

class NotificationSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ["id", "notif_type", "title", "body", "data", "is_read", "created_at"]

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = NotificationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    def list(self, request, *args, **kwargs):
        return success(data=self.get_serializer(self.get_queryset(), many=True).data)
    @action(detail=False, methods=["post"])
    def read_all(self, request):
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return success(message=f"{updated} notification(s) lue(s).")
    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True; notif.save()
        return success(message="Notification lue.")