from django.urls import reverse
from rest_framework import serializers
from .models import BrandApplication


class BrandApplicationInputSerializer(serializers.Serializer):
    authorization_doc = serializers.FileField()
    identity_doc = serializers.FileField()


class BrandApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandApplication
        fields = ["status"]


class BrandApplicationOutSerializer(serializers.ModelSerializer):
    authorization_doc = serializers.SerializerMethodField()
    identity_doc = serializers.SerializerMethodField()
    brand = serializers.StringRelatedField()

    class Meta:
        model = BrandApplication
        fields = [
            "id",
            "authorization_doc",
            "identity_doc",
            "brand_id",
            "brand",
            "distributor_id",
            "request_date",
            "status",
        ]

    def get_authorization_doc(self, obj):
        return obj.authorization_doc.url

    def get_identity_doc(self, obj):
        return obj.identity_doc.url

    def to_representation(self, instance):
        data = super().to_representation(instance)
        self_url = reverse(
            "brand_applications:brand_application", kwargs={"pk": data["id"]}
        )
        brand_url = reverse("brands:brand", kwargs={"pk": data["brand_id"]})
        links = {
            "self": self.context["request"].build_absolute_uri(self_url),
            "brand": self.context["request"].build_absolute_uri(brand_url),
        }

        data["_links"] = links
        return data


class BrandApplicationListOutSerializer(serializers.ModelSerializer):
    """
    Serializer for Brand Application without considering identity_doc 
    and identity_doc to reduce external calls to the Storage service.
    This Serializer is for brand application List.
    """

    brand = serializers.StringRelatedField()

    class Meta:
        model = BrandApplication
        fields = [
            "id",
            "brand_id",
            "brand",
            "distributor_id",
            "request_date",
            "status",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        self_url = reverse(
            "brand_applications:brand_application", kwargs={"pk": data["id"]}
        )
        brand_url = reverse("brands:brand", kwargs={"pk": data["brand_id"]})
        links = {
            "self": self.context["request"].build_absolute_uri(self_url),
            "brand": self.context["request"].build_absolute_uri(brand_url),
        }

        data["_links"] = links
        return data
