from .models import Store

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


