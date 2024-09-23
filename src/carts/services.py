from typing import List
from common.api.exceptions import Conflict
from . import models


class CartItemService:
    def __init__(self) -> None:
        self.selector = CartItemSelector()

    def bulk_create(
        self, product_ids: List[int], customer_id: int, quantity: int = 1
    ) -> None:
        if self.selector.cart_item_exist(
            product_id__in=product_ids, customer_id=customer_id
        ):
            raise Conflict("This Cart Item already exists!")

        cart_items = []
        for product_id in product_ids:

            new_cart_item = models.CartItem(
                product_id=product_id, customer_id=customer_id, quantity=quantity
            )
            new_cart_item.full_clean()
            cart_items.append(new_cart_item)
        
        cart_items = models.CartItem.objects.bulk_create(cart_items)
    
        return cart_items

    def update_quantity(self, cart_item: models.CartItem, quantity: int):
        cart_item.quantity = quantity
        cart_item.full_clean()
        cart_item.save()
    
    def cart_item_delete(self, cart_item: models.CartItem):
        cart_item.delete()

    def clear_cart(self, customer_pk: int):
        models.CartItem.objects.filter(customer_id=customer_pk).delete()
        

class CartItemSelector:
    def cart_item_exist(self, **filters) -> bool:
        is_exist = models.CartItem.objects.filter(**filters).exists()
        return is_exist

    def cart_item_list(self, **filters):
        cart_items = models.CartItem.objects.filter(**filters)
        return cart_items        

