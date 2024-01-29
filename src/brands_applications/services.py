from common.api.exceptions import Conflict
from .models import BrandApplication


class BrandApplicationService:

    def __init__(self) -> None:
        self.selector = BrandApplicationSelector()

    def create(self, **app_data) -> BrandApplication:

        application = BrandApplication(**app_data)
        application.full_clean()

        if self.selector.distributor_has_inprogress_application(application.distributor_id,
                                                                 application.brand_id):
            
            raise Conflict("Current In Progress Application for this brand exists")

        application.save()

        return application


class BrandApplicationSelector:
    def distributor_has_inprogress_application(self, distributor_id, brand_id):

        has_inprogress_app = BrandApplication.objects.filter(
            distributor_id=distributor_id, brand_id=brand_id, status="inprogress"
        ).exists()

        return has_inprogress_app 
