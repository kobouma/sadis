# apps/reviews/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from apps.reviews.models import Like, Review, ReviewImage, ReviewReply


class ReviewImageInline(TabularInline):
    model           = ReviewImage
    extra           = 0
    readonly_fields = ["image"]


class ReviewReplyInline(StackedInline):
    model = ReviewReply
    extra = 0


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    inlines       = [ReviewImageInline, ReviewReplyInline]
    list_display  = ["user", "product", "rating", "created_at"]
    list_filter   = ["rating"]
    search_fields = ["user__phone", "product__name"]


@admin.register(Like)
class LikeAdmin(ModelAdmin):
    list_display  = ["user", "product", "created_at"]
    search_fields = ["user__phone", "product__name"]