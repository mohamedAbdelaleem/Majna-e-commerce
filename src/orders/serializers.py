from django.core.exceptions import ValidationError
from rest_framework import serializers
from addresses.serializers import PickupAddressOutSerializer, StoreOutSerializer
from orders.services import ORDER_STATUS_CHOICES_LIST, OrderSelector
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

    def validate_status(self, val: str):
        if not val:
            return []

        val = val.lower()
        if val not in ORDER_STATUS_CHOICES_LIST:
            raise ValidationError("Invalid status")
        return val



class OrderItemOutSerializer(serializers.ModelSerializer):
    product = ProductListOutSerializer()
    class Meta:
        model = models.OrderItem
        fields = ['quantity', 'unit_price', 'product']


class BaseOrderOutSerializer(serializers.ModelSerializer):
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
        ]

    def get_total_price(self, obj):
        return order_selector.get_order_total_price(obj.pk)
    
    def get_status(self, obj):
        return obj.get_status_display()


class OrderOutSerializer(BaseOrderOutSerializer):
    order_items = OrderItemOutSerializer(many=True, source="orderitem_set")
    class Meta(BaseOrderOutSerializer.Meta):
        fields = BaseOrderOutSerializer.Meta.fields + ['order_items']



class DeliveryOrderListOutSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    class Meta:
        model = models.Order
        fields = [
            "id",
            "customer_id",
            "pickup_address_id",
            "status",
            "ordered_at",
        ]
    
    def get_status(self, obj):
        return obj.get_status_display()


class OrderItemStoresOutSerializer(serializers.ModelSerializer):
    store = StoreOutSerializer()
    class Meta:
        model = models.OrderItemStore
        fields = ['id', 'order_item_id', "store_id", "reserved_quantity", "store"]


class DeliveryOrderItemOutSerializer(serializers.ModelSerializer):
    product = ProductListOutSerializer()
    stores = OrderItemStoresOutSerializer(many=True, source="orderitemstore_set")
    class Meta:
        model = models.OrderItem
        fields = ['quantity', 'unit_price', 'product', 'stores']

class DeliveryOrderOutSerializer(BaseOrderOutSerializer):
    order_items = DeliveryOrderItemOutSerializer(many=True, source="orderitem_set")
    pickup_address = PickupAddressOutSerializer()
    
    class Meta(BaseOrderOutSerializer.Meta):
        fields = BaseOrderOutSerializer.Meta.fields + ['order_items', 'pickup_address']


class OrderStatusInputSerializer(serializers.Serializer):
    status = serializers.CharField()
