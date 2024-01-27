from django.urls import reverse
from django.contrib.auth import get_user_model
from knox.models import AuthToken
from rest_framework.test import APITestCase
from rest_framework import status
from brands.models import Brand


class BrandApplicationTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name="brand")
        cls.url = reverse("brands:brand_applications", kwargs={"pk": cls.brand.pk})
        
        cls.user = get_user_model().objects.create_user(
            email="test@test.com", password="123", email_confirmed=True
        )
        instance, cls.token = AuthToken.objects.create(user=cls.user)

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        
    def test_success_brand_application_upload(self):
        pass

    def test_unauthorized_user_failure(self):
        pass

    def test_forbidden_user_failure(self):
        pass

    def test_max_file_size_exceed_failure(self):
        pass

    def test_invalid_file_format_failure(self):
        pass

    def test_current_inprogress_application_failure(self):
        pass

    def test_invalid_brand_failure(self):
        pass

    def test_invalid_distributor_id_failure(self):
        pass
