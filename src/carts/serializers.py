from rest_framework import serializers
from products.serializers import ProductListOutSerializer
from . import models


class CartItemInputSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField())    


class CartItemOutSerializer(serializers.ModelSerializer):
    product = ProductListOutSerializer()
    class Meta:
        model = models.CartItem
        fields = ['id', 'product', 'customer_id', 'quantity']

    # def to_representation(self, instance):
    #     pass

class CartItemUpdateInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['quantity']
    