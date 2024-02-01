from brands.services import BrandSelector
from common.api.exceptions import Conflict
from .models import BrandApplication


class BrandApplicationService:
    def __init__(self) -> None:
        self.selector = BrandApplicationSelector()

    def create(self, **app_data) -> BrandApplication:
        application = BrandApplication(**app_data)
        application.full_clean()

        if not self.selector.can_upload_application(
            application.distributor_id, application.brand_id
        ):
            raise Conflict(
                "Can't upload due to current in progress application or the distributor already authorized for this brand"
            )

        application.save()

        return application


class BrandApplicationSelector:
    def __init__(self) -> None:
        self.brand_selector = BrandSelector()

    def has_inprogress_applications(self, distributor_id, brand_id):
        has_inprogress_app = BrandApplication.objects.filter(
            distributor_id=distributor_id, brand_id=brand_id, status="inprogress"
        ).exists()
        return has_inprogress_app

    def can_upload_application(self, distributor_id, brand_id):
        currently_distributor = self.brand_selector.has_distributor(
            brand_id, distributor_id
        )

        has_inprogress_application = self.has_inprogress_applications(
            distributor_id, brand_id
        )

        return not has_inprogress_application and not currently_distributor
