from django.urls import path

from apps.reviews.views import LikeToggleView, MyReviewsView, ProductReviewsView, ReviewDetailView, ReviewReplyView
urlpatterns = [
    path("products/<slug:slug>/",                        ProductReviewsView.as_view(), name="product-reviews"),
    path("products/<slug:slug>/like/",                   LikeToggleView.as_view(),     name="product-like"),
    path("products/<slug:slug>/<uuid:review_id>/",       ReviewDetailView.as_view(),   name="review-detail"),
    path("products/<slug:slug>/<uuid:review_id>/reply/", ReviewReplyView.as_view(),    name="review-reply"),
    path("me/",                                          MyReviewsView.as_view(),      name="my-reviews"),
]