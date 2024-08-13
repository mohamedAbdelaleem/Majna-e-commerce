from .models import Store, PickupAddress

class StoreService:
    
    def create_store(self, **store_data):
        store = Store(**store_data)
        store.full_clean()
        store.save()

    def update_store(self, store: Store, **data):
        for key, val in data.items():
            setattr(store, key, val)
        store.full_clean()
        store.save()

class StoreSelector:
    
    def store_list(self, **filters):
        return Store.objects.filter(**filters)
    
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


