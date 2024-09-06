from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from brands.models import Brand
from tests.factories.auth_factories import (
    create_distributor,
    generate_all_users_except,
    generate_auth_token,
    create_groups
)


class CreateBrandApplicationTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.brand = Brand.objects.create(name="brand")
        cls.url = reverse("brands:brand_applications", kwargs={"pk": cls.brand.pk})

        cls.distributor = create_distributor()
        cls.token = generate_auth_token(cls.distributor.user) 

        cls.valid_file = SimpleUploadedFile(
            name="name.pdf",
            content=b"A" * settings.FILE_UPLOAD_MAX_MEMORY_SIZE,
            content_type="application/pdf",
        )

        cls.valid_data = {
            "authorization_doc": cls.valid_file,
            "identity_doc": cls.valid_file,
        }

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_unauthenticated_user_failure(self):
        self.client.credentials()
        data = self.valid_data
        response = self.client.post(
            self.url, data=data, media_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_failure(self):
        users = generate_all_users_except("Distributor")
        for user in users:
            if hasattr(user, "user"):
                token = generate_auth_token(user=user.user)
            else:
                token = generate_auth_token(user=user)

            self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
            response = self.client.post(
                self.url, data=self.valid_data, media_type="multipart/form-data"
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_invalid_brand_failure(self):
        data = self.valid_data
        url = reverse("brands:brand_applications", kwargs={"pk": self.brand.pk + 1})
        response = self.client.post(url, data=data, media_type="multipart/form-data")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
