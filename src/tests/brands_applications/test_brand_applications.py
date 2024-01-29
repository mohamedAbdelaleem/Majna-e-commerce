from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Group
from knox.models import AuthToken
from rest_framework.test import APITestCase
from rest_framework import status
from brands.models import Brand
from accounts.models import Distributor


class BrandApplicationTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name="brand")
        cls.url = reverse("brands:brand_applications", kwargs={"pk": cls.brand.pk})

        cls.user = get_user_model().objects.create_user(
            email="test@test.com", password="123", email_confirmed=True
        )
        Group.objects.create(name="Distributor")
        cls.distributor = Distributor.objects.create_distributor(user=cls.user)

        cls.user2 = get_user_model().objects.create_user(
            email="test2@test.com", password="123", email_confirmed=True
        )

        instance, cls.token = AuthToken.objects.create(user=cls.user)
        instance, cls.token2 = AuthToken.objects.create(user=cls.user2)

        cls.valid_file = SimpleUploadedFile(
            name="name.pdf",
            content=b'A' * settings.FILE_UPLOAD_MAX_MEMORY_SIZE,
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

        cls.valid_data = {
            'authorization_doc': cls.valid_file,
            "identity_doc": cls.valid_file,
        }

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        

    def test_unauthorized_user_failure(self):
        self.client.credentials()
        data = self.valid_data
        response = self.client.post(self.url, data=data, media_type='multipart/form-data')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_user_failure(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        data = self.valid_data
        response = self.client.post(self.url, data=data, media_type='multipart/form-data')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_invalid_brand_failure(self):
        data = self.valid_data
        url = reverse("brands:brand_applications", kwargs={"pk": self.brand.pk+1})
        response = self.client.post(url, data=data, media_type='multipart/form-data')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


