from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.brand_related_factories import BrandApplicationFactory
from utils.tests import (
    create_customer,
    create_distributor,
    create_reviewer,
    generate_auth_token,
    create_groups,
)

class UpdateBrandApplicationForReviewingTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.reviewer = create_reviewer(email="test@test.com")
        cls.token = generate_auth_token(user=cls.reviewer)
        cls.distributor = create_distributor(email="distributor@test.com")
        cls.application = BrandApplicationFactory.create(distributor=cls.distributor)
        cls.url = reverse(
            "brand_applications:brand_application", kwargs={"pk": cls.application.pk}
        )
        cls.approved_data = {'status': 'approved'}
        cls.rejected_update_data = {'status': 'rejected'}

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_unauthorized_user_failure(self):
        self.client.credentials()
        response = self.client.patch(self.url, data=self.approved_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_reviewer_failure(self):
        customer = create_customer(email="test2@test.com")
        token = generate_auth_token(user=customer.user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.patch(self.url, data=self.approved_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        distributor = create_distributor(email="test3@test.com")
        token = generate_auth_token(user=distributor.user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.patch(self.url, data=self.approved_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success_approved_update(self):

        response = self.client.patch(self.url, data=self.approved_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "approved")

        brand = self.application.brand
        distributor_exists = brand.distributors.filter(pk=self.distributor.pk).exists()
        self.assertTrue(distributor_exists)

    def test_success_reject_update(self):

        response = self.client.patch(self.url, data=self.rejected_update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "rejected")

        brand = self.application.brand
        distributor_exists = brand.distributors.filter(pk=self.distributor.pk).exists()
        self.assertFalse(distributor_exists)

    def test_already_reviewed_failure(self):
        application = BrandApplicationFactory.create(distributor=self.distributor)
        url = reverse(
            "brand_applications:brand_application", kwargs={"pk": application.pk}
        )
        
        response = self.client.patch(url, data=self.approved_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(url, data=self.rejected_update_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_invalid_status_failure(self):
        data = {'status': "anything"}
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "inprogress")