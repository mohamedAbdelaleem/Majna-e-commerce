from pathlib import Path
from django.db import models
from brands.models import Brand
from accounts.models import Distributor



BRAND_APPLICATION_CHOICES = [
    ("inprogress", "In Progress"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]


class BrandApplication(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    authorization_doc = models.FileField(
        upload_to=Path("brandApplications/authDocs/%Y/%m/%d")
    )
    identity_doc = models.FileField(
        upload_to=Path("brandApplications/identityDocs/%Y/%m/%d")
    )
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=BRAND_APPLICATION_CHOICES)