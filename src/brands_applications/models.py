from django.db import models
from django.utils import timezone
from brands.models import Brand
from accounts.models import Distributor
from common import validators


def current_date_path(instance, filename):
    current_timestamp = timezone.now()
    date = current_timestamp.strftime('%Y/%m/%d')
    return f"brandApplications/authDocs/{date}/{current_timestamp.time()}_{filename}"


BRAND_APPLICATION_CHOICES = [
    ("inprogress", "In Progress"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]


class BrandApplication(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    authorization_doc = models.FileField(
        upload_to=current_date_path,
        validators=[validators.max_file_size, validators.pdf_format],
    )
    identity_doc = models.FileField(
        upload_to=current_date_path,
        validators=[validators.max_file_size, validators.pdf_format],
    )
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=BRAND_APPLICATION_CHOICES, default="inprogress"
    )
