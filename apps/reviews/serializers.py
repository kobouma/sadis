from rest_framework import serializers

from apps.reviews.models import Review, ReviewImage, ReviewReply
MAX_IMAGES = 5

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ReviewImage
        fields = ["id", "image", "order"]
        read_only_fields = ["id"]

class ReviewReplySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    class Meta:
        model  = ReviewReply
        fields = ["id", "user_name", "comment", "created_at"]
        read_only_fields = ["id", "user_name", "created_at"]

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_id   = serializers.UUIDField(source="user.id",        read_only=True)
    images    = ReviewImageSerializer(many=True, read_only=True)
    reply     = ReviewReplySerializer(read_only=True)
    is_mine   = serializers.SerializerMethodField()
    class Meta:
        model  = Review
        fields = ["id", "user_name", "user_id", "rating", "comment",
                  "images", "reply", "is_mine", "created_at", "updated_at"]
    def get_is_mine(self, obj):
        request = self.context.get("request")
        return bool(request and obj.user == request.user)

class ReviewCreateSerializer(serializers.Serializer):
    rating  = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True)
    images  = serializers.ListField(child=serializers.ImageField(),
                                    required=False, max_length=MAX_IMAGES)
    def validate(self, data):
        user    = self.context["request"].user
        product = self.context["product"]
        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Vous avez déjà laissé un avis.")
        return data
    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        review = Review.objects.create(user=self.context["request"].user,
                                       product=self.context["product"],
                                       rating=validated_data["rating"],
                                       comment=validated_data.get("comment", ""))
        for idx, img in enumerate(images_data):
            ReviewImage.objects.create(review=review, image=img, order=idx)
        return review

class ReviewUpdateSerializer(serializers.Serializer):
    rating           = serializers.IntegerField(min_value=1, max_value=5, required=False)
    comment          = serializers.CharField(required=False, allow_blank=True)
    images           = serializers.ListField(child=serializers.ImageField(), required=False)
    delete_image_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    def validate(self, data):
        review    = self.context["review"]
        remaining = review.images.count() - len(data.get("delete_image_ids",[])) + len(data.get("images",[]))
        if remaining > MAX_IMAGES:
            raise serializers.ValidationError(f"Maximum {MAX_IMAGES} photos par avis.")
        return data
    def update(self, review, validated_data):
        if "rating"  in validated_data: review.rating  = validated_data["rating"]
        if "comment" in validated_data: review.comment = validated_data["comment"]
        review.save()
        ReviewImage.objects.filter(review=review,
                                   id__in=validated_data.get("delete_image_ids",[])).delete()
        from django.db.models import Max
        max_order = review.images.aggregate(m=Max("order"))["m"] or -1
        for idx, img in enumerate(validated_data.get("images", [])):
            ReviewImage.objects.create(review=review, image=img, order=max_order+1+idx)
        return review
