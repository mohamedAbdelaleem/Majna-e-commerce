from rest_framework import serializers
from reviews.models import Review


class ReviewInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "content"]


class ReviewOutputSerializer(serializers.ModelSerializer):
    customer_username = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "content",
            "customer_id",
            "customer_username",
            "product_id",
            "order_date",
            "review_date"
        ]

    def get_customer_username(self, obj):
        return obj.customer.user.username
