from .models import Brand, BrandDistributors


class BrandSelector:

    def brand_list(self):
        return Brand.objects.all()
    
    def has_distributor(self, brand_id, distributor_id):
        return BrandDistributors.objects.filter(brand_id=brand_id, distributor_id=distributor_id).exists()
