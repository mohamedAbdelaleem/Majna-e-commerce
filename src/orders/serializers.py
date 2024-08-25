from rest_framework import serializers
from products.serializers import ProductListOutSerializer
from . import models


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = models.OrderItem
        fields = ['product_id', 'quantity']


class OrderInputSerializer(serializers.Serializer):
    order_items = serializers.ListField(child=OrderItemSerializer())
    pickup_address_id = serializers.IntegerField()


class OrderItemOutSerializer(serializers.ModelSerializer):
    product = ProductListOutSerializer()
    class Meta:
        model = models.OrderItem
        fields = ['product', 'quantity', 'unit_price']


class OrderOutSerializer(serializers.ModelSerializer):
    order_items = serializers.ListField(child=OrderItemOutSerializer())
    class Meta:
        model = models.Order
        fields = [
            "id",
            "customer_id",
            "pickup_address_id",
            "status",
            "ordered_at",
            "order_items"
        ]
