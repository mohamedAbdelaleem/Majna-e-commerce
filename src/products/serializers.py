from rest_framework import serializers
from brands.models import Brand
from . import models


class AlbumItemInputSerializer(serializers.Serializer):
    image = serializers.FileField()
    is_cover = serializers.BooleanField()


class InventoryInputSerializer(serializers.ModelSerializer):
    store_pk = serializers.IntegerField(min_value=1)    # Not PrimaryKeyRelatedField. Validations are applied in the product service to reduce the number of queries
    class Meta:
        model = models.Inventory
        fields = ["store_pk", "quantity"]


class ProductInputSerializer(serializers.ModelSerializer):
    album = AlbumItemInputSerializer(many=True)
    inventory = InventoryInputSerializer(many=True)
    brand_pk = serializers.IntegerField(min_value=1)    # Not PrimaryKeyRelatedField. Validations are applied in the product service to ensure that the distributor has an authorization
    sub_category_pk = serializers.PrimaryKeyRelatedField(
        queryset=models.SubCategory.objects.all(), source='sub_category', write_only=True
    )

    class Meta:
        model = models.Product
        fields = [
            "title",
            "description",
            "price",
            "sub_category_pk",
            "brand_pk",
            "album",
            "inventory",
        ]
