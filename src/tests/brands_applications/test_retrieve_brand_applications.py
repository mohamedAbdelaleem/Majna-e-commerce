from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories.brand_related_factories import BrandApplicationFactory
from tests.factories.auth_factories import (
    create_customer,
    create_distributor,
    create_reviewer,
    generate_auth_token,
    create_groups,
)


class RetrieveBrandApplicationsForReviewingTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.reviewer = create_reviewer(email="test@test.com")
        cls.token = generate_auth_token(user=cls.reviewer)
        cls.url = reverse("brand_applications:brand_applications")

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_unauthorized_user_failure(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_reviewer_failure(self):
        customer = create_customer(email="test2@test.com")
        token = generate_auth_token(user=customer.user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        distributor = create_distributor(email="test3@test.com")
        token = generate_auth_token(user=distributor.user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("results", response.data)


class RetrieveBrandApplicationForReviewingTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.reviewer = create_reviewer(email="test@test.com")
        cls.token = generate_auth_token(user=cls.reviewer)
        distributor = create_distributor(email="distributor@test.com")
        cls.application = BrandApplicationFactory.create(distributor=distributor)
        cls.url = reverse(
            "brand_applications:brand_application", kwargs={"pk": cls.application.pk}
        )

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_unauthorized_user_failure(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_reviewer_failure(self):
        customer = create_customer(email="test2@test.com")
        token = generate_auth_token(user=customer.user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        distributor = create_distributor(email="test3@test.com")
        token = generate_auth_token(user=distributor.user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual("inprogress", response.data['status'])
