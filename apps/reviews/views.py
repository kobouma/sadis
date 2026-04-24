from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from apps.reviews.models import Like, Review, ReviewReply
from apps.reviews.serializers import ReviewCreateSerializer, ReviewReplySerializer, ReviewSerializer, ReviewUpdateSerializer
from core.utils.response import success, created, error

def get_product(slug):
    from apps.products.models import Product
    try: return Product.objects.get(slug=slug)
    except Product.DoesNotExist: return None

class ProductReviewsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, slug):
        product = get_product(slug)
        if not product: return error("Produit introuvable.", status_code=status.HTTP_404_NOT_FOUND)
        reviews = Review.objects.filter(product=product).select_related("user","reply__user")
        agg     = reviews.aggregate(avg=Avg("rating"), total=Count("id"))
        likes   = Like.objects.filter(product=product).count()
        is_liked = Like.objects.filter(product=product, user=request.user).exists() \
                   if request.user.is_authenticated else False
        breakdown = {str(i): reviews.filter(rating=i).count() for i in range(1, 6)}
        return success(data={"stats": {"average_rating": round(agg["avg"] or 0, 1),
                                        "total_reviews": agg["total"], "total_likes": likes,
                                        "is_liked": is_liked, "rating_breakdown": breakdown},
                             "reviews": ReviewSerializer(reviews, many=True, context={"request": request}).data})
    def post(self, request, slug):
        product = get_product(slug)
        if not product: return error("Produit introuvable.", status_code=status.HTTP_404_NOT_FOUND)
        s = ReviewCreateSerializer(data=request.data, context={"request": request, "product": product})
        s.is_valid(raise_exception=True)
        return created(data=ReviewSerializer(s.save(), context={"request": request}).data, message="Avis publié.")

class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def _get(self, slug, review_id, user):
        try: return Review.objects.get(id=review_id, product__slug=slug, user=user)
        except Review.DoesNotExist: return None
    def patch(self, request, slug, review_id):
        review = self._get(slug, review_id, request.user)
        if not review: return error("Avis introuvable.", status_code=status.HTTP_404_NOT_FOUND)
        s = ReviewUpdateSerializer(data=request.data, partial=True,
                                   context={"request": request, "review": review})
        s.is_valid(raise_exception=True)
        return success(data=ReviewSerializer(s.update(review, s.validated_data),
                                             context={"request": request}).data, message="Avis mis à jour.")
    def delete(self, request, slug, review_id):
        review = self._get(slug, review_id, request.user)
        if not review: return error("Avis introuvable.", status_code=status.HTTP_404_NOT_FOUND)
        review.delete()
        return success(message="Avis supprimé.")

class ReviewReplyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, slug, review_id):
        try:
            review = Review.objects.select_related("product__shop__owner").get(id=review_id, product__slug=slug)
        except Review.DoesNotExist: return error("Avis introuvable.", status_code=status.HTTP_404_NOT_FOUND)
        if review.product.shop.owner != request.user:
            return error("Réservé au vendeur.", status_code=status.HTTP_403_FORBIDDEN)
        if hasattr(review, "reply"): return error("Vous avez déjà répondu à cet avis.")
        s = ReviewReplySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        reply = ReviewReply.objects.create(review=review, user=request.user, comment=s.validated_data["comment"])
        return created(data=ReviewReplySerializer(reply).data, message="Réponse publiée.")

class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, slug):
        product = get_product(slug)
        if not product: return error("Produit introuvable.", status_code=status.HTTP_404_NOT_FOUND)
        like, is_new = Like.objects.get_or_create(user=request.user, product=product)
        total = Like.objects.filter(product=product).count()
        if not is_new:
            like.delete()
            return success(data={"liked": False, "total_likes": total - 1}, message="Like retiré.")
        return success(data={"liked": True, "total_likes": total}, message="Produit liké.")

class MyReviewsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        reviews = Review.objects.filter(user=request.user).select_related("product","reply")
        return success(data=ReviewSerializer(reviews, many=True, context={"request": request}).data)
