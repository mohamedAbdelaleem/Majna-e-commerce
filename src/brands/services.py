from accounts.models import Distributor
from .models import Brand, BrandDistributors


class BrandSelector:

    def brand_list(self, **filters):
        return Brand.objects.filter(**filters)
    
    def has_distributor(self, brand_id, distributor_id):
        return BrandDistributors.objects.filter(brand_id=brand_id, distributor_id=distributor_id).exists()


class BrandService:

    def add_distributor(self, brand: Brand, distributor: Distributor):
        brand.distributors.add(distributor)
        brand.save()
        
