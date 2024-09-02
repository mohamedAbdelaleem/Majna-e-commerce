from django.core.exceptions import ValidationError
from rest_framework import serializers
from orders.services import ORDER_CHOICES_MAPPING, OrderSelector
from products.serializers import ProductListOutSerializer
from . import models


order_selector = OrderSelector()

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
        fields = ['quantity', 'unit_price', 'product']


class OrderOutSerializer(serializers.ModelSerializer):
    order_items = OrderItemOutSerializer(many=True, source="orderitem_set")
    total_price = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    class Meta:
        model = models.Order
        fields = [
            "id",
            "customer_id",
            "pickup_address_id",
            "status",
            "ordered_at",
            "total_price",
            "order_items"
        ]

    def get_total_price(self, obj):
        return order_selector.get_order_total_price(obj.pk)
    
    def get_status(self, obj):
        return ORDER_CHOICES_MAPPING[obj.status]


class OrderListQueryParametersSerializer(serializers.Serializer):
    ordering = serializers.CharField(required=False)
    status = serializers.CharField(required=False)

    def validate_ordering(self, val):
        ordering_attributes = ["ordered_at", "-ordered_at"]
        if not val:
            return []
        ordering_list = val.split(",")
        for item in ordering_list:
            if item not in ordering_attributes:
                raise ValidationError("Invalid Ordering attributes")
        return ordering_list

    def validate_status(self, val):
        if not val:
            return []

        if val not in ORDER_CHOICES_MAPPING.values():
            raise ValidationError("Invalid status")

        for key, value in ORDER_CHOICES_MAPPING.items():
            if value == val:
                return key
