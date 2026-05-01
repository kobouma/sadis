# apps/chat/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from apps.chat.views import ConversationViewSet, MessageViewSet

# Router principal
router = DefaultRouter()
router.register(r'', ConversationViewSet, basename='conversation')

# Router imbriqué : /chat/<conversation_pk>/messages/
conv_router = nested_routers.NestedDefaultRouter(
    router, r'', lookup='conversation'
)
conv_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conv_router.urls)),
]