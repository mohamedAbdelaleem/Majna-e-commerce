from django.urls import reverse
from rest_framework import serializers
from .services import BrandApplicationSelector
from .models import BrandApplication


brand_application_selector = BrandApplicationSelector()


class BrandApplicationInputSerializer(serializers.Serializer):
    authorization_doc = serializers.FileField()
    identity_doc = serializers.FileField()


class BrandApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandApplication
        fields = ['status']

class BrandApplicationOutSerializer(serializers.ModelSerializer):
    authorization_doc = serializers.SerializerMethodField()
    identity_doc = serializers.SerializerMethodField()
    class Meta:
        model = BrandApplication
        fields = [
            "id",
            "authorization_doc",
            "identity_doc",
            "brand_id",
            "distributor_id",
            "request_date",
            "status",
        ]


    def get_authorization_doc(self, obj):
        path = obj.authorization_doc
        return brand_application_selector.get_document_url(path)
    
    def get_identity_doc(self, obj):
        path = obj.identity_doc
        return brand_application_selector.get_document_url(path)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        self_url = reverse("brand_applications:brand_application", kwargs={'pk': data['id']})
        brand_url = reverse("brands:brand", kwargs={'pk': data['brand_id']})
        links = {
            'self': self.context['request'].build_absolute_uri(self_url),
            'brand': self.context['request'].build_absolute_uri(brand_url),
            # 'distributor'
        }

        data["_links"] = links
        return data