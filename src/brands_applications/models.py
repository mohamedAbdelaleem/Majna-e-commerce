from django.db import models
from brands.models import Brand
from accounts.models import Distributor
from common.validators import validate_file_size
from utils.helpers import generate_dated_filepath


BRAND_APPLICATION_CHOICES = [
    ("inprogress", "In Progress"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]


def brand_application_doc_path(instance, filename):
    return f"brand_applications/{generate_dated_filepath(filename)}"

class BrandApplication(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    authorization_doc = models.FileField(upload_to=brand_application_doc_path, validators=[validate_file_size])
    identity_doc = models.FileField(upload_to=brand_application_doc_path, validators=[validate_file_size])
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=BRAND_APPLICATION_CHOICES, default="inprogress"
    )
