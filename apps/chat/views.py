# apps/chat/views.py

from django.db import models as django_models
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from apps.products.models import Product


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = ConversationSerializer

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            django_models.Q(buyer=user) | django_models.Q(seller=user)
        ).select_related('buyer', 'seller', 'product').order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        buyer      = request.user
        product_id = request.data.get('product_id')
        seller_id  = request.data.get('seller')
        shop_slug  = request.data.get('shop_slug')

        # Résoudre le seller depuis le produit si non fourni
        if not seller_id and product_id:
            try:
                product   = Product.objects.select_related('shop__owner').get(pk=product_id)
                seller_id = str(product.shop.owner.id)
            except Product.DoesNotExist:
                pass

        # Résoudre depuis le shop_slug si toujours pas trouvé
        if not seller_id and shop_slug:
            from apps.shops.models import Shop
            try:
                shop      = Shop.objects.select_related('owner').get(slug=shop_slug)
                seller_id = str(shop.owner.id)
            except Shop.DoesNotExist:
                pass

        if not seller_id:
            return Response(
                {'error': 'Vendeur introuvable.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            seller = User.objects.get(pk=seller_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Vendeur introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if seller == buyer:
            return Response(
                {'error': 'Vous ne pouvez pas discuter avec vous-même.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupérer ou créer la conversation
        product_obj = None
        if product_id:
            try:
                product_obj = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                pass

        conv, created = Conversation.objects.get_or_create(
            buyer   = buyer,
            seller  = seller,
            product = product_obj,
        )

        return Response(
            {'success': True, 'data': ConversationSerializer(conv).data},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = MessageSerializer

    def get_queryset(self):
        conv_id = self.kwargs.get('conversation_pk')
        return Message.objects.filter(
            conversation_id=conv_id
        ).select_related('sender').order_by('created_at')