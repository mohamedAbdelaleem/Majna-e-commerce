from django.urls import reverse
from rest_framework import serializers
from .models import Brand


class BrandOutSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Brand
        fields = ["id", "name"]


    def to_representation(self, instance):
        data = super().to_representation(instance)

        brand_url = reverse("brands:brand", kwargs={'pk': data['id']})
        applications_collection = reverse("brands:brand_applications", kwargs={'pk': data['id']})
        links = {
            'self': self.context['request'].build_absolute_uri(brand_url),
            # 'collection/applications': self.context['request'].build_absolute_uri(applications_collection),
            # 'collection/distributors'
        }

        data["_links"] = links
        return data

