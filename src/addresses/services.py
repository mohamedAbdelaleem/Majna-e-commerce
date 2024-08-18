from django.db.models import Sum
from common.api.exceptions import Conflict
from .models import Store, PickupAddress
from products.models import Inventory


class StoreService:
    
    def __init__(self) -> None:
        self.selector = StoreSelector()

    def create_store(self, **store_data):
        store = Store(**store_data)
        store.full_clean()
        store.save()

    def update_store(self, store: Store, **data):
        for key, val in data.items():
            setattr(store, key, val)
        store.full_clean()
        store.save()

    def delete_store(self, store: Store):
        if not self.selector.is_empty(store.pk):
            raise Conflict("Products are associated with this Store")
        store.delete()
                

class StoreSelector:
    def store_list(self, **filters):
        return Store.objects.filter(**filters)
    
    def is_empty(self, store_pk: int):
        total_inventory = Inventory.objects.filter(store_id=store_pk).aggregate(
            total=Sum("quantity", default=0)
        )["total"]

        return total_inventory == 0

class PickupAddressService:
    def create_pickup_address(self, **pickup_address_data):
        pickup_address = PickupAddress(**pickup_address_data)
        pickup_address.full_clean()
        pickup_address.save()

    def update_pickup_address(self, pickup_address: PickupAddress, **data):
        for key, val in data.items():
            setattr(pickup_address, key, val)
        pickup_address.full_clean()
        pickup_address.save()

    def delete_pickup_address(self, pickup_address: PickupAddress):
        pickup_address.delete()


class PickupAddressSelector:
    def pickup_address_list(self, **filters):
        return PickupAddress.objects.filter(**filters)
