from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from . import models
from . import services


product_selector = services.ProductSelector()

class AlbumItemInputSerializer(serializers.Serializer):
    image = serializers.FileField()
    is_cover = serializers.BooleanField()


class InventoryInputSerializer(serializers.ModelSerializer):
    store_pk = serializers.IntegerField(min_value=1)    # Not PrimaryKeyRelatedField. Validations are applied in the product service to reduce the number of queries
    class Meta:
        model = models.Inventory
        fields = ["store_pk", "quantity"]


class ProductInputSerializer(serializers.ModelSerializer):
    album = serializers.ListField(child=AlbumItemInputSerializer())
    inventory = serializers.ListField(child=InventoryInputSerializer())
    brand_pk = serializers.IntegerField(min_value=1)    # Not PrimaryKeyRelatedField. Validations are applied in the product service to ensure that the distributor has an authorization
    sub_category_pk = serializers.PrimaryKeyRelatedField(
        queryset=models.SubCategory.objects.all(), source='sub_category', write_only=True
    )

    class Meta:
        model = models.Product
        fields = [
            "name",
            "description",
            "price",
            "sub_category_pk",
            "brand_pk",
            "album",
            "inventory",
        ]


class CategoryOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ["id", "name"]


class SubCategoryOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubCategory
        fields = ["id", "name", "category_id"]

class ProductListQueryParametersSerializer(serializers.Serializer):
    search = serializers.CharField(required=False)
    ordering = serializers.CharField(required=False)
    price__range = serializers.CharField(required=False)
    sub_category_id = serializers.IntegerField(required=False)

    def validate_ordering(self, val):
        ordering_attributes = ['price', '-price']
        if not val:
            return []
        ordering_list = val.split(',')
        for item in ordering_list:
            if item not in ordering_attributes:
                raise ValidationError('Invalid Ordering attributes')
        return ordering_list
    
    def validate_price__range(self, val):
        if not val:
            return []
        
        p_range = val.split(',')
        if len(p_range) != 2:
            raise ValidationError("Price range should be 2 values")
        
        p_range = [float(p_range[0]), float(p_range[1])]
        p_range.sort()
        if p_range[0] < 0:
            raise ValidationError("Invalid Price Values")
        
        return p_range


class ProductListOutSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField()
    cover_image = serializers.SerializerMethodField()
    class Meta:
        model = models.Product
        fields = ['id', 'name', 'price', 'brand', 'cover_image']
    
    def get_cover_image(self, obj):
        # image_url = product_selector.get_cover_image_url(obj.pk)      # After migrating to AWS return the original image
        temp_url = "https://www.mountaingoatsoftware.com/uploads/blog/2016-09-06-what-is-a-product.png"
        return temp_url
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        brand_url = reverse("brands:brand", kwargs={'pk':instance.brand_id})
        links = {
            'brand': self.context["request"].build_absolute_uri(brand_url),
        }

        data['_links'] = links
        return data
    
class FavoriteItemInputSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField())


class FavoriteItemOutSerializer(serializers.ModelSerializer):
    product = ProductListOutSerializer()
    class Meta:
        model = models.FavoriteItem
        fields = ['id', 'product', 'customer_id'] 
   
    def to_representation(self, instance):
        data = super().to_representation(instance)
        links = {}
        data['_links'] = links
        return data