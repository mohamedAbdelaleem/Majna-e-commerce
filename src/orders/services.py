from typing import List, Dict
from collections import deque
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, F
from common.api.exceptions import Conflict
from products.services import ProductSelector
from products.models import Inventory
from addresses.models import PickupAddress
from .models import Order, OrderItem, OrderItemStore


MAX_ORDER_PRODUCTS = 5


ORDER_STATUS_CHOICES_LIST = ["placed", "shipped", "delivered"]

class OrderService:
    def __init__(self) -> None:
        self.product_selector = ProductSelector()
        self.order_selector = OrderSelector()

    def create(self, **order_data: Dict):
        self._validate_order_items(order_data["order_items"])
        self._validate_pickup_address(
            order_data["customer_id"], order_data["pickup_address_id"]
        )

        with transaction.atomic():
            order = Order.objects.create(
                customer_id=order_data["customer_id"],
                pickup_address_id=order_data["pickup_address_id"],
            )
            for order_item in order_data["order_items"]:
                product_id, quantity = order_item["product_id"], order_item["quantity"]
                product = self.product_selector.get_product(pk=product_id)
                new_order_item = OrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    unit_price=product.price,
                    quantity=quantity,
                )
                self._assign_stores(new_order_item, quantity)

    def update_status(self, order: Order, status: str):
        curr_status, status = order.status, status.lower()
        if status in ORDER_STATUS_CHOICES_LIST:
            curr_index = ORDER_STATUS_CHOICES_LIST.index(curr_status)
            status_index = ORDER_STATUS_CHOICES_LIST.index(status)
            if status_index - curr_index != 1:
                raise Conflict("Status should be updated to only the next stage")
        order.status = status
        order.full_clean()
        order.save()

    def _assign_stores(self, order_item: OrderItem, quantity: int):
        inventories = deque(
            self.order_selector.get_available_inventories(order_item.product_id)
        )
        order_item_stores = []
        inventories_update_list = []
        while quantity > 0 and inventories:
            curr_inventory = inventories.popleft()
            reserved_quantity = min(quantity, curr_inventory.quantity)
            order_item_store = OrderItemStore(
                order_item=order_item,
                reserved_quantity=reserved_quantity,
                store_id=curr_inventory.store_id,
            )
            quantity -= reserved_quantity
            curr_inventory.quantity -= reserved_quantity
            inventories_update_list.append(curr_inventory)
            order_item_stores.append(order_item_store)

        OrderItemStore.objects.bulk_create(order_item_stores)
        Inventory.objects.bulk_update(inventories_update_list, ['quantity'])

    def _validate_order_items(self, order_items: List):
        if len(order_items) > MAX_ORDER_PRODUCTS:
            raise ValidationError("Max order items allowed exceeded")
        
        for order_item in order_items:
            product_id, quantity = order_item["product_id"], order_item["quantity"]
            total_inventory = self.product_selector.get_total_quantity(product_id)
            if not total_inventory or total_inventory < quantity:
                raise ValidationError("Not Enough inventory exist")

    def _validate_pickup_address(self, customer_pk: int, pickup_address_pk: int):
        if not PickupAddress.objects.filter(
            customer_id=customer_pk, id=pickup_address_pk
        ).exists():
            raise ValidationError("Invalid Pickup Address")


class OrderSelector:

    def order_list(self, ordering: List[str]=None, **filters): 
        orders = Order.objects.filter(**filters)
        if ordering:
            orders = orders.order_by(*ordering)
        return orders

    def get_order_total_price(self, order_pk: int):
        total_price = OrderItem.objects.filter(order_id=order_pk).aggregate(
            total=Sum(F('quantity') * F("unit_price"), default=0)
        )["total"]
        return total_price

    def get_available_inventories(self, product_id: int):
        inventories = Inventory.objects.filter(product_id=product_id).order_by(
            "-quantity"
        )
        return inventories
