from datetime import timedelta
from django.core.files import File
from brands.services import BrandSelector, BrandService
from common.api.exceptions import Conflict
from common.validators import validate_file_format, validate_file_size
from utils.storage import SupabaseStorageService
from utils.helpers import generate_dated_filepath, hash_filename
from .models import BrandApplication


class BrandApplicationService:
    def __init__(self) -> None:
        self.selector = BrandApplicationSelector()
        self.brand_service = BrandService()
        self.supabase = SupabaseStorageService()

    def create(
        self, authorization_doc: File, identity_doc: File, **app_data
    ) -> BrandApplication:
        self._validate_document(authorization_doc)
        self._validate_document(identity_doc)

        application = BrandApplication(
            authorization_doc=authorization_doc,
            identity_doc=identity_doc,
            **app_data,
        )
        application.full_clean()

        if not self.selector.can_upload_application(
            application.distributor_id, application.brand_id
        ):
            raise Conflict(
                "Can't upload due to current in progress application or the distributor already authorized for this brand"
            )

        application.save()

        return application

    def _validate_document(self, doc: File):
        validate_file_format(doc, ["pdf"])

    def update_status(self, application: BrandApplication, status: str) -> None:

        if application.status != "inprogress":
            raise Conflict("This Application has been already reviewed")
        
        application.status = status
        application.full_clean()
        application.save()
        if application.status == 'approved':
            self.brand_service.add_distributor(application.brand, application.distributor)


class BrandApplicationSelector:
    def __init__(self) -> None:
        self.brand_selector = BrandSelector()
        self.supabase = SupabaseStorageService()

    def brand_application_list(self, **filters):
        result = BrandApplication.objects.filter(**filters)
        return result

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
