from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from brands_applications.services import BrandApplicationSelector
from tests.factories.brand_related_factories import BrandApplicationFactory
from utils.tests import (
    create_customer,
    create_distributor,
    create_reviewer,
    generate_auth_token,
    create_groups,
)


class DistributorBrandsApplicationsListTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_groups()
        cls.distributor = create_distributor(email="distributor@test.com")
        cls.distributor2 = create_distributor(email="distributor2@test.com")
        cls.token = generate_auth_token(user=cls.distributor.user)
        cls.brand_application = BrandApplicationFactory.create(
            distributor=cls.distributor
        )
        cls.brand_application = BrandApplicationFactory.create(
            distributor=cls.distributor2
        )

        cls.url = reverse(
            "distributors:brands_applications", kwargs={"pk": cls.distributor.pk}
        )

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_unauthorized_user_failure(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_distributor_failure(self):
        customer = create_customer(email="customer@test.com")
        token = generate_auth_token(user=customer.user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        reviewer = create_reviewer(email="reviewer@test.com")
        token = generate_auth_token(user=reviewer)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_same_user_failure(self):
        distributor = self.distributor2
        token = generate_auth_token(user=distributor.user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success_brands_applications_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        selector = BrandApplicationSelector()
        distributor_brands_applications = selector.brand_application_list(
            distributor__pk=self.distributor.pk
        ).values_list('id', flat=True)
        for brand_application in response.data:
            self.assertIn(brand_application['id'], distributor_brands_applications)
