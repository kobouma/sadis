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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        buyer      = request.user
        product_id = request.data.get('product_id')
        seller_id  = request.data.get('seller')
        shop_slug  = request.data.get('shop_slug')

        if not seller_id and product_id:
            try:
                product   = Product.objects.select_related('shop__owner').get(pk=product_id)
                seller_id = str(product.shop.owner.id)
            except Product.DoesNotExist:
                pass

        if not seller_id and shop_slug:
            from apps.shops.models import Shop
            try:
                shop      = Shop.objects.select_related('owner').get(slug=shop_slug)
                seller_id = str(shop.owner.id)
            except Shop.DoesNotExist:
                pass

        if not seller_id:
            return Response(
                {'success': False, 'error': 'Vendeur introuvable.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            seller = User.objects.get(pk=seller_id)
        except User.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Vendeur introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if seller == buyer:
            return Response(
                {'success': False, 'error': 'Vous ne pouvez pas discuter avec vous-même.'},
                status=status.HTTP_400_BAD_REQUEST
            )

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

        serializer = ConversationSerializer(
            conv, context={'request': request}
        )
        return Response(
            {'success': True, 'data': serializer.data},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = MessageSerializer

    def get_queryset(self):
        conv_id = self.kwargs.get('conversation_pk')
        user    = self.request.user
        # Vérifier que l'utilisateur fait partie de la conversation
        return Message.objects.filter(
            conversation_id=conv_id,
            conversation__in=Conversation.objects.filter(
                django_models.Q(buyer=user) | django_models.Q(seller=user)
            )
        ).select_related('sender').order_by('created_at')

    def create(self, request, *args, **kwargs):
        conv_id = self.kwargs.get('conversation_pk')
        user    = self.request.user

        # Vérifier accès à la conversation
        try:
            conv = Conversation.objects.get(
                django_models.Q(buyer=user) | django_models.Q(seller=user),
                pk=conv_id,
            )
        except Conversation.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Conversation introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        msg_type = request.data.get('msg_type', 'text')
        payload  = request.data.get('payload', {})

        # Accepter aussi content direct pour compatibilité
        if not payload and request.data.get('content'):
            payload = {'content': request.data.get('content')}

        msg = Message.objects.create(
            conversation = conv,
            sender       = user,
            msg_type     = msg_type,
            payload      = payload,
        )

        # Mettre à jour updated_at de la conversation
        conv.save(update_fields=['updated_at'])

        return Response(
            {'success': True, 'data': MessageSerializer(msg).data},
            status=status.HTTP_201_CREATED
        )