from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.conf import settings
from brands.models import Brand
from accounts.models import Distributor
from brands_applications.models import BrandApplication


class BrandApplicationTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name="brand")
        cls.user = get_user_model().objects.create_user(
            email="test@test.com", password="123", email_confirmed=True
        )
        Group.objects.create(name="Distributor")
        cls.distributor = Distributor.objects.create_distributor(user=cls.user)

        cls.valid_file = SimpleUploadedFile(
            name="name.pdf",
            content=b"A" * settings.FILE_UPLOAD_MAX_MEMORY_SIZE,
            content_type="application/pdf",
        )

        cls.invalid_file_size = SimpleUploadedFile(
            name="name.pdf",
            content=b"A" * (settings.FILE_UPLOAD_MAX_MEMORY_SIZE + 1),
            content_type="application/pdf",
        )
        cls.invalid_file_formate = SimpleUploadedFile(
            name="name.text",
            content=b"A" * settings.FILE_UPLOAD_MAX_MEMORY_SIZE,
            content_type="text/plain",
        )

    def test_max_file_size_exceed_failure(self):
        application = BrandApplication(
            distributor=self.distributor,
            brand=self.brand,
            authorization_doc=self.invalid_file_size,
            identity_doc=self.valid_file,
        )

        with self.assertRaises(ValidationError):
            application.full_clean()

        application = BrandApplication(
            distributor=self.distributor,
            brand=self.brand,
            authorization_doc=self.valid_file,
            identity_doc=self.invalid_file_size,
        )
        with self.assertRaises(ValidationError):
            application.full_clean()


    def test_invalid_file_format_failure(self):
        application = BrandApplication(
            distributor=self.distributor,
            brand=self.brand,
            authorization_doc=self.invalid_file_formate,
            identity_doc=self.valid_file,
        )

        with self.assertRaises(ValidationError):
            application.full_clean()

        application = BrandApplication(
            distributor=self.distributor,
            brand=self.brand,
            authorization_doc=self.valid_file,
            identity_doc=self.invalid_file_formate,
        )
        with self.assertRaises(ValidationError):
            application.full_clean()

