from rest_framework import serializers
from reviews.models import Review


class ReviewInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "content"]


class ReviewOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"

