from .models import Brand


class BrandSelector:

    def brand_list(self):
        return Brand.objects.all()